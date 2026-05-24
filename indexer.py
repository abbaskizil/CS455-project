from sentence_transformers import SentenceTransformer
import chromadb
import shutil

# Download the model once
bi_encoder_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient("./chroma_db")
collection = chroma_client.get_or_create_collection(name="function_collection")

def Encode_Functions(function_list):
    # Calculate embeddings by calling model.encode()
    function_content_list = [f["function_content"] for f in function_list]
    embeddings = bi_encoder_model.encode(function_content_list, show_progress_bar=True)
    print("\nEMBEDDING...")
    return embeddings


def Save_Vectors_In_Database(function_list, function_embeddings):
    # !! if more than nearly 5000 functions, then add by batches
    collection.add(
        ids = [f"{f['function_name']}-{f['start_line']}-{f['end_line']}" for f in function_list],
        documents = [f["function_content"] for f in function_list],
        embeddings = function_embeddings,
        metadatas = [{k: v for k, v in f.items() if k != "function_content"} for f in function_list]
    )
    print("\nSAVING...\n")


def Is_Collection_Empty():
    return collection.count() == 0


def Clear_Collection():
    global collection # to change the value of global collection variable, in python when do collection =, it auto assign collection as local var
    chroma_client.delete_collection("function_collection")
    shutil.rmtree("chroma_db/", ignore_errors=True)
    collection = chroma_client.get_or_create_collection("function_collection")