import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from app.main import app
from app.models.library import Library

client = TestClient(app)

@pytest.fixture
def test_library():
    return Library(
        id=uuid4(),
        name="Test Library",
        documents=[],
        metadata={"key": "value"}
    )

def test_create_library_success(test_library):
    with patch('app.services.library_service.LibraryService.create_library', return_value=test_library):
        response = client.post(
            "/api/libraries",
            headers={"X-API-Version": "1.0"},
            json={"name": "Test Library", "metadata": {"key": "value"}}
        )
        
        assert response.status_code == 201
        assert response.json()["id"] == str(test_library.id)
        assert response.json()["name"] == test_library.name
        assert response.json()["metadata"] == test_library.metadata

def test_create_library_validation_error():
    with patch('app.services.library_service.LibraryService.create_library', 
               side_effect=ValueError("Test validation error")):
        response = client.post(
            "/api/libraries",
            headers={"X-API-Version": "1.0"},
            json={"name": "Test Library", "metadata": {"key": "value"}}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Test validation error"

def test_get_all_libraries(test_library):
    with patch('app.services.library_service.LibraryService.get_all_libraries', 
               return_value=[test_library]):
        response = client.get(
            "/api/libraries",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(test_library.id)
        assert response.json()[0]["name"] == test_library.name

def test_get_all_libraries_empty():
    with patch('app.services.library_service.LibraryService.get_all_libraries', 
               return_value=[]):
        response = client.get(
            "/api/libraries",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 0

def test_get_library_success(test_library):
    with patch('app.services.library_service.LibraryService.get_library', 
               return_value=test_library):
        response = client.get(
            f"/api/libraries/{test_library.id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == str(test_library.id)
        assert response.json()["name"] == test_library.name
        assert response.json()["metadata"] == test_library.metadata

def test_get_library_not_found():
    library_id = uuid4()
    with patch('app.services.library_service.LibraryService.get_library', 
               return_value=None):
        response = client.get(
            f"/api/libraries/{library_id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Library with ID {library_id} not found"

def test_update_library_success(test_library):
    updated_library = Library(
        id=test_library.id,
        name="Updated Library",
        documents=[],
        metadata={"updated": "true"}
    )
    
    with patch('app.services.library_service.LibraryService.update_library', 
               return_value=updated_library):
        response = client.patch(
            f"/api/libraries/{test_library.id}",
            headers={"X-API-Version": "1.0"},
            json={"name": "Updated Library", "metadata": {"updated": "true"}}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == str(updated_library.id)
        assert response.json()["name"] == "Updated Library"
        assert response.json()["metadata"] == {"updated": "true"}

def test_update_library_not_found():
    library_id = uuid4()
    with patch('app.services.library_service.LibraryService.update_library', 
               return_value=None):
        response = client.patch(
            f"/api/libraries/{library_id}",
            headers={"X-API-Version": "1.0"},
            json={"name": "Updated Library"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Library with ID {library_id} not found"

def test_update_library_validation_error(test_library):
    with patch('app.services.library_service.LibraryService.update_library', 
               side_effect=ValueError("Cannot update documents through library update")):
        response = client.patch(
            f"/api/libraries/{test_library.id}",
            headers={"X-API-Version": "1.0"},
            json={"documents": []}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot update documents through library update"

def test_delete_library_success(test_library):
    with patch('app.services.library_service.LibraryService.delete_library', 
               return_value=True):
        response = client.delete(
            f"/api/libraries/{test_library.id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 204
        assert response.text == ""

def test_delete_library_not_found():
    library_id = uuid4()
    with patch('app.services.library_service.LibraryService.delete_library', 
               return_value=False):
        response = client.delete(
            f"/api/libraries/{library_id}",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"Library with ID {library_id} not found"

def test_api_version_validation():
    response = client.get(
        "/api/libraries",
        headers={"X-API-Version": "2.0"}
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "API version 2.0 not supported. Current version: 1.0"

def test_api_version_not_required():
    with patch('app.services.library_service.LibraryService.get_all_libraries', 
               return_value=[]):
        response = client.get("/api/libraries")
        
        assert response.status_code == 200 