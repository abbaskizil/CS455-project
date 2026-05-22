from sentence_transformers import SentenceTransformer

# Download the model once
bi_encoder_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def Encode_Functions(function_list):
    # Calculate embeddings by calling model.encode()
    function_content_list = [f["function_content"] for f in function_list]
    embeddings = bi_encoder_model.encode(function_content_list, show_progress_bar=True)
    return embeddings