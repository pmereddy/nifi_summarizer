import requests
import logging


class OllamaClient:
    def __init__(self, host: str, model: str):
        self.url = f"{host}/api/generate"
        self.model = model

    def generate(self, prompt: str) -> str:
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False
        }
        try:
            resp = requests.post(self.url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get('response', '').strip()
        except Exception as e:
            logging.error(f"LLM generation failed: {e}")
            raise
