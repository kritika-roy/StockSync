import requests
from openai import OpenAI


def call_llm(provider, api_key, base_url, model_name, prompt):

    try:

        # ---------- OPENAI ----------
        if provider == "openai":

            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful business analytics assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content

        # ---------- GROQ ----------
        elif provider == "groq":

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }

            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )

            result = response.json()

            # Handle API errors
            if "error" in result:
                return f"Groq API Error: {result['error']}"

            return result["choices"][0]["message"]["content"]

        else:
            return "Unsupported provider"

    except Exception as e:
        return f"LLM Error: {str(e)}"