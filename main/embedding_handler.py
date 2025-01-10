import requests
import numpy as np
from config import OLLAMA_HOST, MODEL_NAME

class EmbeddingHandler:
    def __init__(self):
        self.base_url = OLLAMA_HOST

    def get_embedding(self, text):
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": MODEL_NAME, "prompt": text}
        )
        embedding = response.json()['embedding']
        return np.array(embedding, dtype=np.float32)
