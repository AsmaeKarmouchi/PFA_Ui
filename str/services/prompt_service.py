# services/prompt_service.py
from services.api_service import get_api_client, get_completion

def reformulate_text(text, pre_prompt=None, model="deepseek/deepseek-r1:free", temperature=0.7, max_tokens=1000):
    """Reformule un texte en utilisant l'API OpenRouter."""
    client = get_api_client()
    prompt = f"{pre_prompt}\n\n{text}" if pre_prompt else text
    return get_completion(client, prompt, model, temperature, max_tokens)