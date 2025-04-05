import pytest
from uuid import uuid4
from app.database.chunk_db import (
    create_chunk,
    get_chunk,
    get_all_chunks,
    get_chunks_by_document,
    update_chunk,
    delete_chunk,
    delete_chunks_by_document
)
from app.models.chunk import Chunk

def test_create_chunk(reset_db, sample_document):
    reset_db.documents[sample_document.id] = sample_document.model_dump()
    
    chunk = Chunk(
        document_id=sample_document.id,
        text="Test chunk",
        embedding=[0.1, 0.2, 0.3],
        metadata={"source": "test"}
    )
    
    created_chunk = create_chunk(chunk)
    
    assert created_chunk.id == chunk.id
    assert created_chunk.text == "Test chunk"
    assert created_chunk.document_id == sample_document.id
    assert chunk.id in reset_db.chunks
    assert reset_db.chunk_document_map[chunk.id] == sample_document.id

def test_create_chunk_with_nonexistent_document(reset_db):
    chunk = Chunk(
        document_id=uuid4(),
        text="Test chunk",
        embedding=[0.1, 0.2, 0.3],
        metadata={"source": "test"}
    )
    
    with pytest.raises(ValueError, match="Document .* does not exist"):
        create_chunk(chunk)

def test_get_chunk(populated_db, sample_chunk):
    retrieved_chunk = get_chunk(sample_chunk.id)
    
    assert retrieved_chunk is not None
    assert retrieved_chunk.id == sample_chunk.id
    assert retrieved_chunk.text == sample_chunk.text
    assert retrieved_chunk.document_id == sample_chunk.document_id

def test_get_nonexistent_chunk(reset_db):
    retrieved_chunk = get_chunk(uuid4())
    
    assert retrieved_chunk is None

def test_get_all_chunks(populated_db, sample_chunk):
    chunks = get_all_chunks()
    
    assert len(chunks) == 1
    assert chunks[0].id == sample_chunk.id

def test_get_chunks_by_document(populated_db, sample_chunk, sample_document_id):
    chunks = get_chunks_by_document(sample_document_id)
    
    assert len(chunks) == 1
    assert chunks[0].id == sample_chunk.id
    
    empty_chunks = get_chunks_by_document(uuid4())
    assert len(empty_chunks) == 0

def test_update_chunk(populated_db, sample_chunk):
    chunk_id = sample_chunk.id
    update_data = {"text": "Updated chunk text", "metadata": {"updated": "true"}}
    
    updated_chunk = update_chunk(chunk_id, update_data)
    
    assert updated_chunk is not None
    assert updated_chunk.text == "Updated chunk text"
    assert updated_chunk.metadata == {"updated": "true"}
    
    assert populated_db.chunks[chunk_id]["text"] == "Updated chunk text"

def test_update_nonexistent_chunk(reset_db):
    updated_chunk = update_chunk(uuid4(), {"text": "New text"})
    
    assert updated_chunk is None

def test_update_chunk_document_id(populated_db, sample_chunk):
    with pytest.raises(ValueError, match="Cannot change document_id"):
        update_chunk(sample_chunk.id, {"document_id": uuid4()})

def test_delete_chunk(populated_db, sample_chunk):
    result = delete_chunk(sample_chunk.id)
    
    assert result is True
    assert sample_chunk.id not in populated_db.chunks
    assert sample_chunk.id not in populated_db.chunk_document_map

def test_delete_nonexistent_chunk(reset_db):
    result = delete_chunk(uuid4())
    
    assert result is False

def test_delete_chunks_by_document(populated_db, sample_chunk, sample_document_id):
    count = delete_chunks_by_document(sample_document_id)
    
    assert count == 1
    assert sample_chunk.id not in populated_db.chunks
    assert sample_chunk.id not in populated_db.chunk_document_map
    
    count = delete_chunks_by_document(uuid4())
    assert count == 0 