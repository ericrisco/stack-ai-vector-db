import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from app.models.library import Library
from app.models.document import Document
from app.models.chunk import Chunk
from app.services.document_service import DocumentService

@pytest.fixture
def sample_library_id():
    return uuid4()

@pytest.fixture
def sample_document_id():
    return uuid4()

@pytest.fixture
def sample_document(sample_document_id, sample_library_id):
    return Document(
        id=sample_document_id,
        library_id=sample_library_id,
        name="Test Document",
        chunks=[],
        metadata={"key": "value"}
    )

@pytest.fixture
def sample_documents(sample_library_id):
    return [
        Document(
            id=uuid4(),
            library_id=sample_library_id,
            name=f"Test Document {i}",
            chunks=[],
            metadata={"index": str(i)}
        )
        for i in range(3)
    ]

@pytest.fixture
def sample_chunk(sample_document_id):
    return Chunk(
        id=uuid4(),
        document_id=sample_document_id,
        text="Test chunk content",
        embedding=[0.1, 0.2, 0.3, 0.4],
        metadata={"key": "value"}
    )

@pytest.fixture
def sample_chunks(sample_document_id):
    return [
        Chunk(
            id=uuid4(),
            document_id=sample_document_id,
            text=f"Test chunk content {i}",
            embedding=[0.1 * i, 0.2 * i, 0.3 * i, 0.4 * i],
            metadata={"index": str(i)}
        )
        for i in range(3)
    ]

@pytest.fixture
def sample_document_with_chunks(sample_document, sample_chunks):
    document = Document(
        id=sample_document.id,
        library_id=sample_document.library_id,
        name=sample_document.name,
        chunks=sample_chunks,
        metadata=sample_document.metadata
    )
    return document

@patch('app.services.document_service.create_document')
def test_create_document(mock_create_document, sample_document):
    mock_create_document.return_value = sample_document
    
    result = DocumentService.create_document(sample_document)
    
    assert result == sample_document
    mock_create_document.assert_called_once_with(sample_document)

@patch('app.services.document_service.create_document')
def test_create_documents(mock_create_document, sample_documents):
    mock_create_document.side_effect = lambda doc: doc
    
    result = DocumentService.create_documents(sample_documents)
    
    assert len(result) == len(sample_documents)
    assert result == sample_documents
    assert mock_create_document.call_count == len(sample_documents)

@patch('app.services.document_service.get_document')
def test_get_document(mock_get_document, sample_document):
    mock_get_document.return_value = sample_document
    
    result = DocumentService.get_document(sample_document.id)
    
    assert result == sample_document
    mock_get_document.assert_called_once_with(sample_document.id)

@patch('app.services.document_service.get_document')
def test_get_nonexistent_document(mock_get_document):
    document_id = uuid4()
    mock_get_document.return_value = None
    
    result = DocumentService.get_document(document_id)
    
    assert result is None
    mock_get_document.assert_called_once_with(document_id)

@patch('app.services.document_service.get_all_documents')
def test_get_all_documents(mock_get_all_documents, sample_documents):
    mock_get_all_documents.return_value = sample_documents
    
    result = DocumentService.get_all_documents()
    
    assert result == sample_documents
    mock_get_all_documents.assert_called_once()

@patch('app.services.document_service.get_documents_by_library')
def test_get_documents_by_library(mock_get_documents_by_library, sample_documents, sample_library_id):
    mock_get_documents_by_library.return_value = sample_documents
    
    result = DocumentService.get_documents_by_library(sample_library_id)
    
    assert result == sample_documents
    mock_get_documents_by_library.assert_called_once_with(sample_library_id)

@patch('app.services.document_service.update_document')
def test_update_document(mock_update_document, sample_document):
    document_id = sample_document.id
    update_data = {"name": "Updated Document", "metadata": {"updated": "true"}}
    updated_document = Document(
        id=document_id,
        library_id=sample_document.library_id,
        name="Updated Document",
        chunks=[],
        metadata={"updated": "true"}
    )
    mock_update_document.return_value = updated_document
    
    result = DocumentService.update_document(document_id, update_data)
    
    assert result == updated_document
    mock_update_document.assert_called_once_with(document_id, update_data)

def test_update_document_with_chunks():
    document_id = uuid4()
    update_data = {"chunks": []}
    
    with pytest.raises(ValueError, match="Cannot update chunks through this method"):
        DocumentService.update_document(document_id, update_data)

@patch('app.services.document_service.get_document')
@patch('app.services.document_service.get_db')
@patch('app.services.document_service.delete_chunks_by_document')
@patch('app.services.document_service.create_chunk')
def test_update_document_chunks(mock_create_chunk, mock_delete_chunks, mock_get_db, mock_get_document, 
                               sample_document, sample_chunks):
    document_id = sample_document.id
    mock_get_document.return_value = sample_document
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    result = DocumentService.update_document_chunks(document_id, sample_chunks)
    
    mock_get_document.assert_called_once_with(document_id)
    mock_delete_chunks.assert_called_once_with(document_id)
    assert mock_create_chunk.call_count == len(sample_chunks)
    assert result is not None
    assert result.id == document_id
    assert len(result.chunks) == len(sample_chunks)

@patch('app.services.document_service.get_document')
def test_update_chunks_nonexistent_document(mock_get_document, sample_chunks):
    document_id = uuid4()
    mock_get_document.return_value = None
    
    result = DocumentService.update_document_chunks(document_id, sample_chunks)
    
    assert result is None
    mock_get_document.assert_called_once_with(document_id)

@patch('app.services.document_service.delete_document')
def test_delete_document(mock_delete_document, sample_document):
    mock_delete_document.return_value = True
    
    result = DocumentService.delete_document(sample_document.id)
    
    assert result is True
    mock_delete_document.assert_called_once_with(sample_document.id)

@patch('app.services.document_service.delete_document')
def test_delete_nonexistent_document(mock_delete_document):
    document_id = uuid4()
    mock_delete_document.return_value = False
    
    result = DocumentService.delete_document(document_id)
    
    assert result is False
    mock_delete_document.assert_called_once_with(document_id) 