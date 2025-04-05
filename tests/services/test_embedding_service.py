import pytest
import pytest_asyncio
import os
import json
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.embedding_service import EmbeddingService

# Test data 
TEST_TEXT = "This is a test sentence for embedding."
TEST_TEXTS = ["First test sentence.", "Second test sentence."]
MOCK_EMBEDDING = [0.1, 0.2, 0.3, 0.4, 0.5] * 20  # 100-dimensional mock embedding
MOCK_RESPONSE = {
    "embeddings": [MOCK_EMBEDDING]
}
MOCK_BATCH_RESPONSE = {
    "embeddings": [MOCK_EMBEDDING, MOCK_EMBEDDING]
}
TEST_API_KEY = "fake_api_key_for_testing"

@pytest.fixture
def mock_env(monkeypatch):
    """Set up fake API key for testing"""
    monkeypatch.setenv("COHERE_API_KEY", TEST_API_KEY)
    # Also patch the class attribute directly since it might have been loaded before test
    monkeypatch.setattr(EmbeddingService, "COHERE_API_KEY", TEST_API_KEY)
    return TEST_API_KEY

class MockResponse:
    def __init__(self, status_code, json_data, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
    
    def json(self):
        return self._json_data

@pytest_asyncio.fixture
async def mock_httpx_client():
    """Mock for httpx client that returns a successful response with embeddings"""
    with patch('httpx.AsyncClient') as mock_client:
        client_instance = AsyncMock()
        
        # Configure mock post method
        async def mock_post(*args, **kwargs):
            json_data = kwargs.get('json', {})
            texts = json_data.get('texts', [])
            
            if len(texts) > 1:
                return MockResponse(200, MOCK_BATCH_RESPONSE)
            else:
                return MockResponse(200, MOCK_RESPONSE)
        
        # Set the side effect for the post method
        client_instance.post = AsyncMock(side_effect=mock_post)
        
        # Configure the context manager
        mock_client.return_value.__aenter__.return_value = client_instance
        
        yield mock_client

@pytest_asyncio.fixture
async def mock_httpx_client_error():
    """Mock for httpx client that returns an error response"""
    with patch('httpx.AsyncClient') as mock_client:
        client_instance = AsyncMock()
        
        async def mock_error_post(*args, **kwargs):
            return MockResponse(400, {}, "Bad request")
        
        client_instance.post = AsyncMock(side_effect=mock_error_post)
        mock_client.return_value.__aenter__.return_value = client_instance
        
        yield mock_client

@pytest.mark.asyncio
async def test_generate_embedding_single_text(mock_env, mock_httpx_client):
    """Test generating embedding for a single text"""
    embedding = await EmbeddingService.generate_embedding(TEST_TEXT)
    
    # Verify the result is the mock embedding
    assert embedding == MOCK_EMBEDDING
    
    # Verify API was called with correct parameters
    client = mock_httpx_client.return_value.__aenter__.return_value
    called_args = client.post.call_args
    assert called_args[1]['json']['texts'] == [TEST_TEXT]
    assert called_args[1]['json']['model'] == EmbeddingService.DEFAULT_MODEL
    assert called_args[1]['json']['input_type'] == 'search_document'
    
    # Verify headers contain API key
    assert called_args[1]['headers']['Authorization'] == f"Bearer {TEST_API_KEY}"

@pytest.mark.asyncio
async def test_generate_embeddings_multiple_texts(mock_env, mock_httpx_client):
    """Test generating embeddings for multiple texts"""
    embeddings = await EmbeddingService.generate_embeddings(TEST_TEXTS)
    
    # Verify we get two embeddings back
    assert len(embeddings) == 2
    assert embeddings == [MOCK_EMBEDDING, MOCK_EMBEDDING]
    
    # Verify API was called with correct parameters
    client = mock_httpx_client.return_value.__aenter__.return_value
    called_args = client.post.call_args
    assert called_args[1]['json']['texts'] == TEST_TEXTS
    assert called_args[1]['json']['input_type'] == 'search_document'