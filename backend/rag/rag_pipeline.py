from rag.retriever import retrieve_context
from rag.llm_client import call_llm


def run_rag(collection, question, api_key, base_url, model_name, provider):

    context_docs = retrieve_context(collection, question)

    if not context_docs:
        return "Information not available in database."

    context = "\n\n".join(context_docs)

    prompt = f"""
You are an AI assistant helping with business analytics insights.

Use ONLY the context below to answer.

Context:
{context}

Question:
{question}

Rules:
- Do not invent information
- If answer not found say:
"Information not available in database."
"""

    answer = call_llm(
        provider,
        api_key,
        base_url,
        model_name,
        prompt
    )

    return answer