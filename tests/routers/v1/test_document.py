import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from app.main import app
from app.models.document import Document
from app.models.chunk import Chunk

client = TestClient(app)

@pytest.fixture
def test_document():
    return Document(
        id=uuid4(),
        library_id=uuid4(),
        name="Test Document",
        chunks=[],
        metadata={"key": "value"}
    )

def test_create_document_success(test_document):
    with patch('app.services.document_service.DocumentService.create_document', return_value=test_document):
        response = client.post(
            "/api/documents",
            headers={"X-API-Version": "1.0"},
            json={
                "library_id": str(test_document.library_id),
                "name": "Test Document", 
                "metadata": {"key": "value"}
            }
        )
        
        assert response.status_code == 201
        assert response.json()["id"] == str(test_document.id)
        assert response.json()["name"] == test_document.name
        assert response.json()["metadata"] == test_document.metadata

def test_create_document_validation_error():
    with patch('app.services.document_service.DocumentService.create_document', 
               side_effect=ValueError("Test validation error")):
        response = client.post(
            "/api/documents",
            headers={"X-API-Version": "1.0"},
            json={
                "library_id": str(uuid4()),
                "name": "Test Document", 
                "metadata": {"key": "value"}
            }
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Test validation error"

def test_get_all_documents(test_document):
    with patch('app.services.document_service.DocumentService.get_all_documents', 
               return_value=[test_document]):
        response = client.get(
            "/api/documents",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(test_document.id)
        assert response.json()[0]["name"] == test_document.name

def test_get_all_documents_empty():
    with patch('app.services.document_service.DocumentService.get_all_documents', 
               return_value=[]):
        response = client.get(
            "/api/documents",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 0

def test_get_documents_by_library(test_document):
    library_id = test_document.library_id
    with patch('app.services.document_service.DocumentService.get_documents_by_library', 
               return_value=[test_document]):
        response = client.get(
            f"/api/documents/library/{library_id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(test_document.id)
        assert response.json()[0]["name"] == test_document.name

def test_get_document_success(test_document):
    with patch('app.services.document_service.DocumentService.get_document', 
               return_value=test_document):
        response = client.get(
            f"/api/documents/{test_document.id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == str(test_document.id)
        assert response.json()["name"] == test_document.name
        assert response.json()["metadata"] == test_document.metadata

def test_get_document_not_found():
    document_id = uuid4()
    with patch('app.services.document_service.DocumentService.get_document', 
               return_value=None):
        response = client.get(
            f"/api/documents/{document_id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Document with ID {document_id} not found"

def test_update_document_success(test_document):
    updated_document = Document(
        id=test_document.id,
        library_id=test_document.library_id,
        name="Updated Document",
        chunks=[],
        metadata={"updated": "true"}
    )
    
    with patch('app.services.document_service.DocumentService.update_document', 
               return_value=updated_document):
        response = client.patch(
            f"/api/documents/{test_document.id}",
            headers={"X-API-Version": "1.0"},
            json={"name": "Updated Document", "metadata": {"updated": "true"}}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == str(updated_document.id)
        assert response.json()["name"] == "Updated Document"
        assert response.json()["metadata"] == {"updated": "true"}

def test_update_document_not_found():
    document_id = uuid4()
    with patch('app.services.document_service.DocumentService.update_document', 
               return_value=None):
        response = client.patch(
            f"/api/documents/{document_id}",
            headers={"X-API-Version": "1.0"},
            json={"name": "Updated Document"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Document with ID {document_id} not found"

def test_update_document_validation_error(test_document):
    with patch('app.services.document_service.DocumentService.update_document', 
               side_effect=ValueError("Cannot update chunks through this method")):
        response = client.patch(
            f"/api/documents/{test_document.id}",
            headers={"X-API-Version": "1.0"},
            json={"chunks": []}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot update chunks through this method"

def test_delete_document_success(test_document):
    with patch('app.services.document_service.DocumentService.delete_document', 
               return_value=True):
        response = client.delete(
            f"/api/documents/{test_document.id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 204
        assert response.text == ""

def test_delete_document_not_found():
    document_id = uuid4()
    with patch('app.services.document_service.DocumentService.delete_document', 
               return_value=False):
        response = client.delete(
            f"/api/documents/{document_id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Document with ID {document_id} not found"

def test_api_version_validation():
    response = client.get(
        "/api/documents",
        headers={"X-API-Version": "2.0"}
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "API version 2.0 not supported. Current version: 1.0"

def test_api_version_not_required():
    with patch('app.services.document_service.DocumentService.get_all_documents', 
               return_value=[]):
        response = client.get("/api/documents")
        
        assert response.status_code == 200 