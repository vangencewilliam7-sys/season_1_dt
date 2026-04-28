import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found in environment.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

    def get_embedding(self, text: str, model="text-embedding-3-small"):
        if not self.client: return [0.0] * 1536
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input=[text], model=model).data[0].embedding

    def get_embeddings_batch(self, texts: list[str], model="text-embedding-3-small"):
        if not self.client: return [[0.0] * 1536] * len(texts)
        texts = [t.replace("\n", " ") for t in texts]
        response = self.client.embeddings.create(input=texts, model=model)
        return [d.embedding for d in response.data]
