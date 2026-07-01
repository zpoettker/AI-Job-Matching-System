from abc import ABC, abstractmethod
from openai import OpenAI


class EmbeddingServiceBase(ABC):
    @abstractmethod
    def get_embeddings(self, texts):
        pass


class OpenAIEmbeddingService(EmbeddingServiceBase):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def get_embeddings(self, texts):
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,  # Send all texts at once in a single API call
        )
        return [item.embedding for item in response.data]  # Pull out each vector and return as a list
