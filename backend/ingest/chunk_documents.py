def chunk_documents(documents, chunk_size=500, overlap=100):
    chunks = []

    for doc in documents:
        start = 0
        while start < len(doc):
            end = start + chunk_size
            chunks.append(doc[start:end])
            start += chunk_size - overlap

    return chunks

