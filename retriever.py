import indexer
from sentence_transformers import CrossEncoder

cross_encoder_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

def Encode_Query(query):
    query_embedding = indexer.bi_encoder_model.encode(query)
    return query_embedding


def Query_Collection(query_embedding):
    results = indexer.collection.query(
        query_embeddings = query_embedding,
        n_results = 20
    )
    return results


def Rerank_Functions(query, results):
    function_document_list = results["documents"][0]
    function_metadata_list = results["metadatas"][0]
    ranks = cross_encoder_model.rank(query, function_document_list, return_documents=True)
    reranked_function_list = []
    for idx, rank in enumerate(ranks):
        limit = idx + 1
        function_subdict = {
            "code": rank["text"],
            "function_name": function_metadata_list[rank["corpus_id"]]["function_name"],
            "start_line": function_metadata_list[rank["corpus_id"]]["start_line"],
            "end_line": function_metadata_list[rank["corpus_id"]]["end_line"]
        }
        reranked_function_list.append(function_subdict)
        if limit == 5:
            break
    return reranked_function_list