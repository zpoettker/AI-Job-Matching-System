# Refactoring Report

## SOLID Principles Chosen

1. Single Responsibility Principle (SRP)
2. Dependency Inversion Principle (DIP)

---

## 1. Single Responsibility Principle

### The Problem
The original `main.py` was one file doing everything — fetching jobs from an API, cleaning text, generating embeddings, and scoring results. Any change to any part of the system required touching the same file.

### The Fix
Split the code into 4 dedicated classes, each with one responsibility:

- `JobFetcher` — fetches job listings from the Adzuna API
- `TextPreprocessor` — cleans raw text and extracts resume sections
- `EmbeddingService` — generates embedding vectors via OpenAI
- `JobMatcher` — scores and ranks jobs against the resume

`main.py` now only orchestrates these classes and contains no business logic.

### Before
```python
# Everything in one file
def fetch_jobs(pages):
    ...

def clean_text(text):
    ...

def get_embeddings(texts):
    ...

def cosine_similarity(a, b):
    ...

def main():
    fetch_jobs(...)
    clean_text(...)
    get_embeddings(...)
    cosine_similarity(...)
```

### After
```python
# Each responsibility in its own class
from job_fetcher import JobFetcher
from text_preprocessor import TextPreprocessor
from embedding_service import OpenAIEmbeddingService
from job_matcher import JobMatcher

def main():
    fetcher = JobFetcher(...)
    preprocessor = TextPreprocessor()
    embedder = OpenAIEmbeddingService(...)
    matcher = JobMatcher()
```

---

## 2. Dependency Inversion Principle

### The Problem
After applying SRP, `main.py` still directly instantiated `OpenAIEmbeddingService`, tightly coupling the high-level logic to a specific third-party provider. This made it impossible to test without making real API calls to OpenAI.

### The Fix
Introduced an abstract base class `EmbeddingServiceBase` using Python's `ABC` module. The high-level code now depends on the abstraction, not the concrete implementation. A `MockEmbeddingService` can be injected during tests without changing any other code.

### Before
```python
# Hardcoded dependency on OpenAI
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embeddings(texts):
    response = client.embeddings.create(...)
    return [item.embedding for item in response.data]
```

### After
```python
# Abstract base class defines the contract
from abc import ABC, abstractmethod

class EmbeddingServiceBase(ABC):
    @abstractmethod
    def get_embeddings(self, texts):
        pass

# Concrete implementation fulfills the contract
class OpenAIEmbeddingService(EmbeddingServiceBase):
    def get_embeddings(self, texts):
        ...

# Mock implementation used in tests — no API call needed
class MockEmbeddingService(EmbeddingServiceBase):
    def get_embeddings(self, texts):
        return [[0.0, 0.0, 0.0] for _ in texts]
```
