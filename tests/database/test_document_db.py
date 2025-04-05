import pytest
from uuid import uuid4
from app.database.document_db import (
    create_document,
    get_document,
    get_all_documents,
    get_documents_by_library,
    update_document,
    delete_document,
    delete_documents_by_library
)
from app.models.document import Document
from app.models.chunk import Chunk

def test_create_document(reset_db, sample_library):
    reset_db.libraries[sample_library.id] = sample_library.model_dump()
    
    chunk = Chunk(
        document_id=uuid4(),
        text="Test chunk",
        embedding=[0.1, 0.2, 0.3],
        metadata={"source": "test"}
    )
    
    document = Document(
        library_id=sample_library.id,
        name="Test Document",
        chunks=[chunk],
        metadata={"source": "test"}
    )
    
    created_document = create_document(document)
    
    assert created_document.id == document.id
    assert created_document.name == "Test Document"
    assert created_document.library_id == sample_library.id
    assert document.id in reset_db.documents
    assert reset_db.document_library_map[document.id] == sample_library.id
    
    assert len(created_document.chunks) == 1
    assert created_document.chunks[0].document_id == document.id
    assert len(reset_db.chunks) == 1
    chunk_id = list(reset_db.chunks.keys())[0]
    assert reset_db.chunk_document_map[chunk_id] == document.id

def test_create_document_with_nonexistent_library(reset_db):
    document = Document(
        library_id=uuid4(),
        name="Test Document",
        chunks=[],
        metadata={"source": "test"}
    )
    
    with pytest.raises(ValueError, match="Library .* does not exist"):
        create_document(document)

def test_get_document(populated_db, sample_document):
    retrieved_document = get_document(sample_document.id)
    
    assert retrieved_document is not None
    assert retrieved_document.id == sample_document.id
    assert retrieved_document.name == sample_document.name
    assert retrieved_document.library_id == sample_document.library_id

def test_get_nonexistent_document(reset_db):
    retrieved_document = get_document(uuid4())
    
    assert retrieved_document is None

def test_get_all_documents(populated_db, sample_document):
    documents = get_all_documents()
    
    assert len(documents) == 1
    assert documents[0].id == sample_document.id

def test_get_documents_by_library(populated_db, sample_document, sample_library_id):
    documents = get_documents_by_library(sample_library_id)
    
    assert len(documents) == 1
    assert documents[0].id == sample_document.id
    
    empty_documents = get_documents_by_library(uuid4())
    assert len(empty_documents) == 0

def test_update_document(populated_db, sample_document):
    document_id = sample_document.id
    update_data = {"name": "Updated Document", "metadata": {"updated": "true"}}
    
    updated_document = update_document(document_id, update_data)
    
    assert updated_document is not None
    assert updated_document.name == "Updated Document"
    assert updated_document.metadata == {"updated": "true"}
    
    assert populated_db.documents[document_id]["name"] == "Updated Document"

def test_update_nonexistent_document(reset_db):
    updated_document = update_document(uuid4(), {"name": "New name"})
    
    assert updated_document is None

def test_update_document_library_id(populated_db, sample_document):
    with pytest.raises(ValueError, match="Cannot change library_id"):
        update_document(sample_document.id, {"library_id": uuid4()})

def test_update_document_chunks(populated_db, sample_document):
    with pytest.raises(ValueError, match="Cannot update chunks"):
        update_document(sample_document.id, {"chunks": []})

def test_delete_document(populated_db, sample_document, sample_chunk):
    result = delete_document(sample_document.id)
    
    assert result is True
    assert sample_document.id not in populated_db.documents
    assert sample_document.id not in populated_db.document_library_map
    
    assert sample_chunk.id not in populated_db.chunks
    assert sample_chunk.id not in populated_db.chunk_document_map

def test_delete_nonexistent_document(reset_db):
    result = delete_document(uuid4())
    
    assert result is False

def test_delete_documents_by_library(populated_db, sample_document, sample_chunk, sample_library_id):
    count = delete_documents_by_library(sample_library_id)
    
    assert count == 1
    assert sample_document.id not in populated_db.documents
    assert sample_document.id not in populated_db.document_library_map
    assert sample_chunk.id not in populated_db.chunks
    assert sample_chunk.id not in populated_db.chunk_document_map
    
    count = delete_documents_by_library(uuid4())
    assert count == 0 