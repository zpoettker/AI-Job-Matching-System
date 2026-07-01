from embedding_service import EmbeddingServiceBase

class MockEmbeddingService(EmbeddingServiceBase): # Fake embedding service for testing purposes
    def get_embeddings(self, texts):
        return [[0.0, 0.0, 0.0] for _ in texts] # Instead of calling the real API, just return a list of zero vectors for each text


def test_mock_returns_one_embedding_per_text():
    # The number of embeddings returned should match the number of texts sent
    service = MockEmbeddingService()
    texts = ["hello", "hi", "testing"]
    result = service.get_embeddings(texts)
    assert len(result) == 3 # 3 texts should return 3 embeddings
