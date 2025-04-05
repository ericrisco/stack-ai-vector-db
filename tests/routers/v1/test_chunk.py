import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from app.main import app
from app.models.chunk import Chunk

client = TestClient(app)

@pytest.fixture
def test_chunk():
    return Chunk(
        id=uuid4(),
        document_id=uuid4(),
        text="Test chunk content",
        embedding=[0.1, 0.2, 0.3],
        metadata={"key": "value"}
    )

def test_create_chunk_success(test_chunk):
    with patch('app.services.chunk_service.ChunkService.create_chunk', return_value=test_chunk):
        response = client.post(
            "/api/chunks",
            headers={"X-API-Version": "1.0"},
            json={
                "document_id": str(test_chunk.document_id),
                "text": "Test chunk content",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"key": "value"}
            }
        )
        
        assert response.status_code == 201
        assert response.json()["id"] == str(test_chunk.id)
        assert response.json()["text"] == test_chunk.text
        assert response.json()["embedding"] == test_chunk.embedding
        assert response.json()["metadata"] == test_chunk.metadata

def test_create_chunk_validation_error():
    with patch('app.services.chunk_service.ChunkService.create_chunk', 
               side_effect=ValueError("Test validation error")):
        response = client.post(
            "/api/chunks",
            headers={"X-API-Version": "1.0"},
            json={
                "document_id": str(uuid4()),
                "text": "Test chunk content",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"key": "value"}
            }
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Test validation error"

def test_create_chunks_success(test_chunk):
    chunks = [test_chunk]
    with patch('app.services.chunk_service.ChunkService.create_chunks', return_value=chunks):
        response = client.post(
            "/api/chunks/batch",
            headers={"X-API-Version": "1.0"},
            json=[{
                "document_id": str(test_chunk.document_id),
                "text": "Test chunk content",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"key": "value"}
            }]
        )
        
        assert response.status_code == 201
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(test_chunk.id)
        assert response.json()[0]["text"] == test_chunk.text

def test_create_chunks_validation_error():
    with patch('app.services.chunk_service.ChunkService.create_chunks', 
               side_effect=ValueError("Test validation error")):
        response = client.post(
            "/api/chunks/batch",
            headers={"X-API-Version": "1.0"},
            json=[{
                "document_id": str(uuid4()),
                "text": "Test chunk content",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"key": "value"}
            }]
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Test validation error"

def test_get_all_chunks(test_chunk):
    with patch('app.services.chunk_service.ChunkService.get_all_chunks', 
               return_value=[test_chunk]):
        response = client.get(
            "/api/chunks",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(test_chunk.id)
        assert response.json()[0]["text"] == test_chunk.text

def test_get_all_chunks_empty():
    with patch('app.services.chunk_service.ChunkService.get_all_chunks', 
               return_value=[]):
        response = client.get(
            "/api/chunks",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 0

def test_get_chunks_by_document(test_chunk):
    document_id = test_chunk.document_id
    with patch('app.services.chunk_service.ChunkService.get_chunks_by_document', 
               return_value=[test_chunk]):
        response = client.get(
            f"/api/chunks/document/{document_id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(test_chunk.id)
        assert response.json()[0]["text"] == test_chunk.text

def test_get_chunk_success(test_chunk):
    with patch('app.services.chunk_service.ChunkService.get_chunk', 
               return_value=test_chunk):
        response = client.get(
            f"/api/chunks/{test_chunk.id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == str(test_chunk.id)
        assert response.json()["text"] == test_chunk.text
        assert response.json()["embedding"] == test_chunk.embedding
        assert response.json()["metadata"] == test_chunk.metadata

def test_get_chunk_not_found():
    chunk_id = uuid4()
    with patch('app.services.chunk_service.ChunkService.get_chunk', 
               return_value=None):
        response = client.get(
            f"/api/chunks/{chunk_id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Chunk with ID {chunk_id} not found"

def test_update_chunk_success(test_chunk):
    updated_chunk = Chunk(
        id=test_chunk.id,
        document_id=test_chunk.document_id,
        text="Updated chunk content",
        embedding=[0.3, 0.2, 0.1],
        metadata={"updated": "true"}
    )
    
    with patch('app.services.chunk_service.ChunkService.update_chunk', 
               return_value=updated_chunk):
        response = client.patch(
            f"/api/chunks/{test_chunk.id}",
            headers={"X-API-Version": "1.0"},
            json={
                "text": "Updated chunk content",
                "embedding": [0.3, 0.2, 0.1],
                "metadata": {"updated": "true"}
            }
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == str(updated_chunk.id)
        assert response.json()["text"] == "Updated chunk content"
        assert response.json()["embedding"] == [0.3, 0.2, 0.1]
        assert response.json()["metadata"] == {"updated": "true"}

def test_update_chunk_not_found():
    chunk_id = uuid4()
    with patch('app.services.chunk_service.ChunkService.update_chunk', 
               return_value=None):
        response = client.patch(
            f"/api/chunks/{chunk_id}",
            headers={"X-API-Version": "1.0"},
            json={"text": "Updated chunk content"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Chunk with ID {chunk_id} not found"

def test_update_chunk_validation_error(test_chunk):
    with patch('app.services.chunk_service.ChunkService.update_chunk', 
               side_effect=ValueError("Cannot change document_id of an existing chunk")):
        response = client.patch(
            f"/api/chunks/{test_chunk.id}",
            headers={"X-API-Version": "1.0"},
            json={"document_id": str(uuid4())}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot change document_id of an existing chunk"

def test_delete_chunk_success(test_chunk):
    with patch('app.services.chunk_service.ChunkService.delete_chunk', 
               return_value=True):
        response = client.delete(
            f"/api/chunks/{test_chunk.id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 204
        assert response.text == ""

def test_delete_chunk_not_found():
    chunk_id = uuid4()
    with patch('app.services.chunk_service.ChunkService.delete_chunk', 
               return_value=False):
        response = client.delete(
            f"/api/chunks/{chunk_id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Chunk with ID {chunk_id} not found"

def test_api_version_validation():
    response = client.get(
        "/api/chunks",
        headers={"X-API-Version": "2.0"}
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "API version 2.0 not supported. Current version: 1.0"

def test_api_version_not_required():
    with patch('app.services.chunk_service.ChunkService.get_all_chunks', 
               return_value=[]):
        response = client.get("/api/chunks")
        
        assert response.status_code == 200 