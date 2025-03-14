# services/api_service.py
from openai import OpenAI
from config import API_KEY, BASE_URL

def get_api_client():
    """Retourne un client OpenAI configuré pour OpenRouter."""
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)

def get_completion(client, prompt, model="deepseek/deepseek-r1:free", temperature=0.7, max_tokens=1000):
    """Obtient une réponse du modèle."""
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return completion.choices[0].message.content