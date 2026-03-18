from rag.embeddings import get_embeddings


def retrieve_context(collection, query, top_k=3):

    query_embedding = get_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [])

    if not documents:
        return []

    return documents[0]