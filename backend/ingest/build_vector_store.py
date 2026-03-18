import chromadb
from chromadb.config import Settings
from rag.embeddings import get_embeddings


def build_vector_store(chunks):

    client = chromadb.Client(Settings(
        persist_directory="chroma_db",
        is_persistent=True
    ))

    collection = client.get_or_create_collection(name="business_data")

    # Optional: clear old data to prevent duplicates
    if collection.count() > 0:
        collection.delete(ids=[str(i) for i in range(collection.count())])

    embeddings = get_embeddings(chunks)

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[str(i)],
            metadatas=[{"source": "business_analytics"}]
        )

    return collection