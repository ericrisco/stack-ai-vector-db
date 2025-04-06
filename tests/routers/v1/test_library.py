import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4, UUID
from app.main import app
from app.models.library import Library, IndexStatus, IndexerType
from app.services.library_service import LibraryService

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

def test_delete_library_success():
    # Create a random ID
    library_id = uuid4()
    
    # Mock the service calls
    with patch.object(LibraryService, 'get_library', return_value=Library(id=library_id, name="Test Library")):
        with patch.object(LibraryService, 'delete_library', return_value=True):
            response = client.delete(
                f"/api/libraries/{library_id}",
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

@pytest.mark.asyncio
async def test_start_indexing():
    # Create a random ID
    library_id = uuid4()
    
    # Mock the start_indexing_library method
    mock_result = {
        "status": "indexing_started", 
        "library_id": str(library_id),
        "indexer_type": IndexerType.BRUTE_FORCE
    }
    
    # Create a mock for the async method
    async_mock = AsyncMock(return_value=mock_result)
    
    # Apply the mock
    with patch.object(LibraryService, 'start_indexing_library', async_mock):
        response = client.post(
            f"/api/libraries/{library_id}/index",
            headers={"X-API-Version": "1.0"},
            json={"indexer_type": "BRUTE_FORCE"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "indexing_started"
        assert response.json()["library_id"] == str(library_id)
        assert response.json()["indexer_type"] == "BRUTE_FORCE"

@pytest.mark.asyncio
async def test_start_indexing_invalid_library():
    # Create a random ID
    library_id = uuid4()
    
    # Mock the start_indexing_library method to raise an error
    async_mock = AsyncMock(side_effect=ValueError(f"Library with ID {library_id} not found"))
    
    # Apply the mock
    with patch.object(LibraryService, 'start_indexing_library', async_mock):
        response = client.post(
            f"/api/libraries/{library_id}/index",
            headers={"X-API-Version": "1.0"},
            json={"indexer_type": "BRUTE_FORCE"}
        )
        
        assert response.status_code == 400
        assert f"Library with ID {library_id} not found" in response.json()["detail"]

def test_get_indexing_status():
    # Create a random ID
    library_id = uuid4()
    
    # Mock the get_indexing_status method
    mock_status = {
        "library_id": str(library_id),
        "indexed": True,
        "indexer_type": "BRUTE_FORCE",
        "indexing_in_progress": False,
        "last_indexed": 1234567890.123
    }
    
    # Apply the mock
    with patch.object(LibraryService, 'get_indexing_status', return_value=mock_status):
        response = client.get(
            f"/api/libraries/{library_id}/index/status",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 200
        assert response.json()["library_id"] == str(library_id)
        assert response.json()["indexed"] is True
        assert response.json()["indexer_type"] == "BRUTE_FORCE"
        assert response.json()["indexing_in_progress"] is False
        assert response.json()["last_indexed"] == 1234567890.123

def test_get_indexing_status_not_found():
    # Create a random ID
    library_id = uuid4()
    
    # Mock the get_indexing_status method to raise an error
    with patch.object(LibraryService, 'get_indexing_status', 
                     side_effect=ValueError(f"Library with ID {library_id} not found")):
        response = client.get(
            f"/api/libraries/{library_id}/index/status",
            headers={"X-API-Version": "1.0"}
        )
        
        assert response.status_code == 404
        assert f"Library with ID {library_id} not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_search_library():
    # Create a random ID
    library_id = uuid4()
    
    # Create document and chunk IDs
    document_id = uuid4()
    chunk_id = uuid4()
    
    # Create DocumentInfo and SearchResult models
    from app.models.search import DocumentInfo, SearchResult
    
    document_info = DocumentInfo(
        id=str(document_id),
        name="Test Document",
        metadata={"source": "test"}
    )
    
    search_result = SearchResult(
        chunk_id=str(chunk_id),
        text="This is a test chunk that matches the query",
        score=0.95,
        document=document_info
    )
    
    # Create a mock for the async method
    async_mock = AsyncMock(return_value=[search_result])
    
    # Apply the mock
    with patch.object(LibraryService, 'search_library', async_mock):
        response = client.post(
            f"/api/libraries/{library_id}/search",
            headers={"X-API-Version": "1.0"},
            params={"query_text": "test query", "top_k": 5}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["score"] == 0.95
        assert response.json()[0]["document"]["name"] == "Test Document"
        assert response.json()[0]["text"] == "This is a test chunk that matches the query"

@pytest.mark.asyncio
async def test_search_library_not_indexed():
    # Create a random ID
    library_id = uuid4()
    
    # Mock the search_library method to raise a not indexed error
    error_message = f"Library is not indexed. Please index the library before searching."
    async_mock = AsyncMock(side_effect=ValueError(error_message))
    
    # Apply the mock
    with patch.object(LibraryService, 'search_library', async_mock):
        response = client.post(
            f"/api/libraries/{library_id}/search",
            headers={"X-API-Version": "1.0"},
            params={"query_text": "test query", "top_k": 5}
        )
        
        assert response.status_code == 409
        assert error_message in response.json()["detail"]

@pytest.mark.asyncio
async def test_search_library_indexing_in_progress():
    # Create a random ID
    library_id = uuid4()
    
    # Mock the search_library method to raise an indexing in progress error
    error_message = f"Library is currently being indexed. Please try again later."
    async_mock = AsyncMock(side_effect=ValueError(error_message))
    
    # Apply the mock
    with patch.object(LibraryService, 'search_library', async_mock):
        response = client.post(
            f"/api/libraries/{library_id}/search",
            headers={"X-API-Version": "1.0"},
            params={"query_text": "test query", "top_k": 5}
        )
        
        assert response.status_code == 409
        assert error_message in response.json()["detail"]

@pytest.mark.asyncio
async def test_search_library_not_found():
    # Create a random ID
    library_id = uuid4()
    
    # Mock the search_library method to raise a library not found error
    error_message = f"Library with ID {library_id} not found"
    async_mock = AsyncMock(side_effect=ValueError(error_message))
    
    # Apply the mock
    with patch.object(LibraryService, 'search_library', async_mock):
        response = client.post(
            f"/api/libraries/{library_id}/search",
            headers={"X-API-Version": "1.0"},
            params={"query_text": "test query", "top_k": 5}
        )
        
        assert response.status_code == 404
        assert error_message in response.json()["detail"] 