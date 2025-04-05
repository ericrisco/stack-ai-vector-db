import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from app.models.chunk import Chunk
from app.services.chunk_service import ChunkService

@pytest.fixture
def sample_document_id():
    return uuid4()

@pytest.fixture
def sample_chunk_id():
    return uuid4()

@pytest.fixture
def sample_chunk(sample_chunk_id, sample_document_id):
    return Chunk(
        id=sample_chunk_id,
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

@patch('app.services.chunk_service.get_document')
@patch('app.services.chunk_service.create_chunk')
def test_create_chunk(mock_create_chunk, mock_get_document, sample_chunk):
    mock_get_document.return_value = MagicMock()  
    mock_create_chunk.return_value = sample_chunk
    
    result = ChunkService.create_chunk(sample_chunk)
    
    assert result == sample_chunk
    mock_get_document.assert_called_once_with(sample_chunk.document_id)
    mock_create_chunk.assert_called_once_with(sample_chunk)

@patch('app.services.chunk_service.get_document')
def test_create_chunk_nonexistent_document(mock_get_document, sample_chunk):
    mock_get_document.return_value = None  
    
    with pytest.raises(ValueError, match=f"Document with ID {sample_chunk.document_id} does not exist"):
        ChunkService.create_chunk(sample_chunk)
    mock_get_document.assert_called_once_with(sample_chunk.document_id)

@patch('app.services.chunk_service.get_document')
@patch('app.services.chunk_service.create_chunk')
def test_create_chunks(mock_create_chunk, mock_get_document, sample_chunks):
    mock_get_document.return_value = MagicMock()  
    mock_create_chunk.side_effect = lambda chunk: chunk
    
    result = ChunkService.create_chunks(sample_chunks)
    
    assert len(result) == len(sample_chunks)
    assert result == sample_chunks
    mock_get_document.assert_called_once_with(sample_chunks[0].document_id)
    assert mock_create_chunk.call_count == len(sample_chunks)

def test_create_chunks_empty_list():
    result = ChunkService.create_chunks([])
    
    assert result == []

@patch('app.services.chunk_service.get_document')
def test_create_chunks_nonexistent_document(mock_get_document, sample_chunks):
    mock_get_document.return_value = None  
    
    with pytest.raises(ValueError, match=f"Document with ID {sample_chunks[0].document_id} does not exist"):
        ChunkService.create_chunks(sample_chunks)
    mock_get_document.assert_called_once_with(sample_chunks[0].document_id)

def test_create_chunks_mixed_document_ids(sample_document_id):
    chunks = [
        Chunk(
            id=uuid4(),
            document_id=sample_document_id,
            text="Test chunk 1",
            embedding=[0.1, 0.2, 0.3],
            metadata={}
        ),
        Chunk(
            id=uuid4(),
            document_id=uuid4(),  
            text="Test chunk 2",
            embedding=[0.4, 0.5, 0.6],
            metadata={}
        )
    ]
    
    with pytest.raises(ValueError, match="All chunks must belong to the same document"):
        ChunkService.create_chunks(chunks)

@patch('app.services.chunk_service.get_chunk')
def test_get_chunk(mock_get_chunk, sample_chunk):
    mock_get_chunk.return_value = sample_chunk
    
    result = ChunkService.get_chunk(sample_chunk.id)
    
    assert result == sample_chunk
    mock_get_chunk.assert_called_once_with(sample_chunk.id)

@patch('app.services.chunk_service.get_chunk')
def test_get_nonexistent_chunk(mock_get_chunk):
    chunk_id = uuid4()
    mock_get_chunk.return_value = None
    
    result = ChunkService.get_chunk(chunk_id)
    
    assert result is None
    mock_get_chunk.assert_called_once_with(chunk_id)

@patch('app.services.chunk_service.get_all_chunks')
def test_get_all_chunks(mock_get_all_chunks, sample_chunks):
    mock_get_all_chunks.return_value = sample_chunks
    
    result = ChunkService.get_all_chunks()
    
    assert result == sample_chunks
    mock_get_all_chunks.assert_called_once()

@patch('app.services.chunk_service.get_chunks_by_document')
def test_get_chunks_by_document(mock_get_chunks_by_document, sample_chunks, sample_document_id):
    mock_get_chunks_by_document.return_value = sample_chunks
    
    result = ChunkService.get_chunks_by_document(sample_document_id)
    
    assert result == sample_chunks
    mock_get_chunks_by_document.assert_called_once_with(sample_document_id)

@patch('app.services.chunk_service.update_chunk')
def test_update_chunk(mock_update_chunk, sample_chunk):
    chunk_id = sample_chunk.id
    update_data = {"text": "Updated chunk content", "metadata": {"updated": "true"}}
    updated_chunk = Chunk(
        id=chunk_id,
        document_id=sample_chunk.document_id,
        text="Updated chunk content",
        embedding=sample_chunk.embedding,
        metadata={"updated": "true"}
    )
    mock_update_chunk.return_value = updated_chunk
    
    result = ChunkService.update_chunk(chunk_id, update_data)
    
    assert result == updated_chunk
    mock_update_chunk.assert_called_once_with(chunk_id, update_data)

@patch('app.services.chunk_service.update_chunk')
def test_update_nonexistent_chunk(mock_update_chunk):
    chunk_id = uuid4()
    update_data = {"text": "Updated content"}
    mock_update_chunk.return_value = None
    
    result = ChunkService.update_chunk(chunk_id, update_data)
    
    assert result is None
    mock_update_chunk.assert_called_once_with(chunk_id, update_data)

@patch('app.services.chunk_service.delete_chunk')
def test_delete_chunk(mock_delete_chunk, sample_chunk):
    mock_delete_chunk.return_value = True
    
    result = ChunkService.delete_chunk(sample_chunk.id)
    
    assert result is True
    mock_delete_chunk.assert_called_once_with(sample_chunk.id)

@patch('app.services.chunk_service.delete_chunk')
def test_delete_nonexistent_chunk(mock_delete_chunk):
    chunk_id = uuid4()
    mock_delete_chunk.return_value = False
    
    result = ChunkService.delete_chunk(chunk_id)
    
    assert result is False
    mock_delete_chunk.assert_called_once_with(chunk_id) 