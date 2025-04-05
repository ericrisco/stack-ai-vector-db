import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from app.models.library import Library
from app.models.document import Document
from app.models.chunk import Chunk
from app.services.library_service import LibraryService

@pytest.fixture
def sample_library():
    return Library(
        id=uuid4(),
        name="Test Library",
        documents=[],
        metadata={"key": "value"}
    )

@pytest.fixture
def sample_document():
    return Document(
        id=uuid4(),
        library_id=uuid4(),
        name="Test Document",
        chunks=[],
        metadata={"key": "value"}
    )

@pytest.fixture
def sample_library_with_documents(sample_library, sample_document):
    document = Document(
        id=sample_document.id,
        library_id=sample_library.id,
        name=sample_document.name,
        chunks=sample_document.chunks,
        metadata=sample_document.metadata
    )
    library = Library(
        id=sample_library.id,
        name=sample_library.name,
        documents=[document],
        metadata=sample_library.metadata
    )
    return library

@patch('app.services.library_service.create_library')
def test_create_library(mock_create_library, sample_library):
    mock_create_library.return_value = sample_library
    
    result = LibraryService.create_library(sample_library)
    
    assert result == sample_library
    mock_create_library.assert_called_once_with(sample_library)

@patch('app.services.library_service.get_library')
def test_get_library(mock_get_library, sample_library):
    mock_get_library.return_value = sample_library
    
    result = LibraryService.get_library(sample_library.id)
    
    assert result == sample_library
    mock_get_library.assert_called_once_with(sample_library.id)

@patch('app.services.library_service.get_library')
def test_get_nonexistent_library(mock_get_library):
    mock_get_library.return_value = None
    library_id = uuid4()
    
    result = LibraryService.get_library(library_id)
    
    assert result is None
    mock_get_library.assert_called_once_with(library_id)

@patch('app.services.library_service.get_all_libraries')
def test_get_all_libraries(mock_get_all_libraries, sample_library):
    mock_get_all_libraries.return_value = [sample_library]
    
    result = LibraryService.get_all_libraries()
    
    assert result == [sample_library]
    mock_get_all_libraries.assert_called_once()

@patch('app.services.library_service.update_library')
def test_update_library(mock_update_library, sample_library):
    library_id = sample_library.id
    update_data = {"name": "Updated Library", "metadata": {"updated": "true"}}
    updated_library = Library(
        id=library_id,
        name="Updated Library",
        documents=[],
        metadata={"updated": "true"}
    )
    mock_update_library.return_value = updated_library
    
    result = LibraryService.update_library(library_id, update_data)
    
    assert result == updated_library
    mock_update_library.assert_called_once_with(library_id, update_data)

@patch('app.services.library_service.update_library')
def test_update_nonexistent_library(mock_update_library):
    library_id = uuid4()
    update_data = {"name": "Updated Library"}
    mock_update_library.return_value = None
    
    result = LibraryService.update_library(library_id, update_data)
    
    assert result is None
    mock_update_library.assert_called_once_with(library_id, update_data)

def test_update_library_with_documents():
    library_id = uuid4()
    update_data = {"documents": []}
    
    with pytest.raises(ValueError, match="Cannot update documents through library update"):
        LibraryService.update_library(library_id, update_data)

@patch('app.services.library_service.delete_library')
def test_delete_library(mock_delete_library, sample_library):
    mock_delete_library.return_value = True
    
    result = LibraryService.delete_library(sample_library.id)
    
    assert result is True
    mock_delete_library.assert_called_once_with(sample_library.id)

@patch('app.services.library_service.delete_library')
def test_delete_nonexistent_library(mock_delete_library):
    library_id = uuid4()
    mock_delete_library.return_value = False
    
    result = LibraryService.delete_library(library_id)
    
    assert result is False
    mock_delete_library.assert_called_once_with(library_id) 