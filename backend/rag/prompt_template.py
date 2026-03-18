def build_prompt(context, question):

    prompt = f"""
You are an AI assistant helping with business analytics insights.

Use ONLY the context provided below to answer the question.

Context:
{context}

Question:
{question}

Rules:
- Do not make up information
- If the answer is not in the context say:
"Information not available in database."
"""

    return prompt