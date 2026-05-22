import indexer

def Encode_Query(query):
    query_embedding = indexer.bi_encoder_model.encode(query)
    return query_embedding


def Query_Collection(query_embedding):
    results = indexer.collection.query(
        query_embeddings = query_embedding,
        n_results = 20
    )
    print(results)



query = input("query: ")
embedding = Encode_Query(query)
Query_Collection(embedding)