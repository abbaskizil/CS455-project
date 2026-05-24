# Standard library
import os
import glob
import shutil
import stat
import pathlib
import json

# Third party
from git import Repo
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Local
import chunker
import indexer
import retriever
import generator


# Global Variables
source_code_extensions = (".py", ".ipynb",".cpp", ".c", ".hpp", ".js", ".ts", ".java", ".go")
sessions = {}


# Models
class IndexRequest(BaseModel):
    github_url: str

class ChatRequest(BaseModel):
    query: str
    session_id: str


# App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/index")
def index(request: IndexRequest):
    try:
        Run_Indexing_Pipeline(request.github_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not clone repository: {str(e)}")
    return {"status": "success"}

@app.post("/chat")
def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if indexer.Is_Collection_Empty():
        raise HTTPException(status_code=400, detail="No repository indexed yet")
    response = Run_Chat_Pipeline(request.session_id, request.query)
    return {"response": response}

@app.get("/files")
def files():
    return {"files": Get_Indexed_Files()}


# Functions
def redo_with_write(func, path, exc_info):
    os.chmod(path, stat.S_IWUSR)
    func(path)

def Chunk_Notebook_Functions(file_path, function_list):
    with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
            
    for idx, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            cell_code = "".join(cell["source"])
            cell_metadata = {
                "function_name": f"{file_path}::cell_{idx}",
                "start_line": -1,
                "end_line": -1,
                "function_content": cell_code
            }
            function_list.append(cell_metadata)


def Chunk_Code_File_Functions(file_path, function_list, extension):
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()
    all_chunked_functions = chunker.Function_Parser(file_path, source_code, extension)
    function_list.extend(all_chunked_functions)

def Run_Indexing_Pipeline(github_url):
    indexer.Clear_Collection()
    repo_exists = os.path.isdir("temp/")
    current_directory = pathlib.Path().resolve()
    if not repo_exists:
        repo_dir = "temp/"
        Repo.clone_from(github_url, repo_dir)

    file_list = []
    path_list = [(curDir,fl) for curDir, subDir, files in os.walk("temp/") for fl in files if fl.endswith(source_code_extensions)]
    for f in path_list:
        norm_path = os.path.normpath(os.path.join(current_directory, f[0], f[1]))
        file_list.append(norm_path)

    all_function_list = []
    for file_path in file_list:
        extension = "." + file_path.split(".")[-1]
        if extension == ".ipynb":
            Chunk_Notebook_Functions(file_path, all_function_list)
        else:
            Chunk_Code_File_Functions(file_path, all_function_list, extension)

    # Remove repo after creating all_function_list
    shutil.rmtree("temp/", onerror = redo_with_write)

    # If collection does not exist, create and save embeddings inside it 
    is_collection_empty = indexer.Is_Collection_Empty()
    if (is_collection_empty):
        embeddings = indexer.Encode_Functions(all_function_list)
        indexer.Save_Vectors_In_Database(all_function_list, embeddings)

def Run_Chat_Pipeline(session_id, query):
    chat_history = sessions.get(session_id, [])
    # bi_encoder + cross_encoder - retrieve related functions
    query_embedding = retriever.Encode_Query(query)
    top20_related_functions = retriever.Query_Collection(query_embedding)
    reranked_function_list = retriever.Rerank_Functions(query, top20_related_functions)

    # generator part
    context_string = generator.Dict_To_Context_String_Converter(reranked_function_list)
    user_prompt = generator.Build_User_Prompt(query, context_string)
    response, chat_history = generator.Chat(user_prompt, chat_history)
    sessions[session_id] = chat_history
    return response

def Get_Indexed_Files():
    results = indexer.collection.get()
    file_names = set()
    for metadata in results["metadatas"]:
        function_name = metadata["function_name"]
        file_path = function_name.split("::")[0]
        file_name = os.path.basename(file_path)
        file_names.add(file_name)
    return list(file_names)