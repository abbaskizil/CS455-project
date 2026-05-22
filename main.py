# Standard library
import os
import glob
import shutil
import stat
import pathlib
import json

# Third party
from git import Repo

# Local
import chunker
import indexer

# GLOBAL VARIABLES
current_directory = pathlib.Path().resolve()
repo_exists = os.path.isdir("temp/")
source_code_extensions = (".py", ".ipynb",".cpp", ".c", ".hpp", ".js", ".ts", ".java", ".go")

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


if __name__ == "__main__":
    # Clone the repo you want
    if not repo_exists:
        git_url = "https://github.com/omuremreyildiz03/spotify-wrap-demo"
        repo_dir = "temp/"
        Repo.clone_from(git_url, repo_dir)

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


    # will be continued