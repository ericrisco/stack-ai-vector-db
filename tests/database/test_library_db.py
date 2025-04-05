import pytest
from uuid import uuid4
from app.database.library_db import (
    create_library,
    get_library,
    get_all_libraries,
    update_library,
    delete_library
)
from app.models.library import Library
from app.models.document import Document
from app.models.chunk import Chunk

def test_create_library(reset_db):
    chunk = Chunk(
        document_id=uuid4(),
        text="Test chunk",
        embedding=[0.1, 0.2, 0.3],
        metadata={"source": "test"}
    )
    
    document = Document(
        library_id=uuid4(),
        name="Test Document",
        chunks=[chunk],
        metadata={"source": "test"}
    )
    
    library = Library(
        name="Test Library",
        documents=[document],
        metadata={"source": "test"}
    )
    
    created_library = create_library(library)
    
    assert created_library.id == library.id
    assert created_library.name == "Test Library"
    assert library.id in reset_db.libraries
    
    assert len(created_library.documents) == 1
    document_id = created_library.documents[0].id
    assert document_id in reset_db.documents
    assert reset_db.document_library_map[document_id] == library.id
    
    assert len(created_library.documents[0].chunks) == 1
    chunk_id = created_library.documents[0].chunks[0].id
    assert chunk_id in reset_db.chunks
    assert reset_db.chunk_document_map[chunk_id] == document_id

def test_create_library_already_exists(reset_db, sample_library):
    reset_db.libraries[sample_library.id] = sample_library.model_dump()
    
    with pytest.raises(ValueError, match="Library with ID .* already exists"):
        create_library(sample_library)

def test_get_library(populated_db, sample_library):
    retrieved_library = get_library(sample_library.id)
    
    assert retrieved_library is not None
    assert retrieved_library.id == sample_library.id
    assert retrieved_library.name == sample_library.name

def test_get_nonexistent_library(reset_db):
    retrieved_library = get_library(uuid4())
    
    assert retrieved_library is None

def test_get_all_libraries(populated_db, sample_library):
    libraries = get_all_libraries()
    
    assert len(libraries) == 1
    assert libraries[0].id == sample_library.id

def test_update_library(populated_db, sample_library):
    library_id = sample_library.id
    update_data = {"name": "Updated Library", "metadata": {"updated": "true"}}
    
    updated_library = update_library(library_id, update_data)
    
    assert updated_library is not None
    assert updated_library.name == "Updated Library"
    assert updated_library.metadata == {"updated": "true"}
    
    assert populated_db.libraries[library_id]["name"] == "Updated Library"

def test_update_nonexistent_library(reset_db):
    updated_library = update_library(uuid4(), {"name": "New name"})
    
    assert updated_library is None

def test_update_library_documents(populated_db, sample_library):
    with pytest.raises(ValueError, match="Cannot update documents"):
        update_library(sample_library.id, {"documents": []})

def test_delete_library(populated_db, sample_library, sample_document, sample_chunk):
    result = delete_library(sample_library.id)
    
    assert result is True
    assert sample_library.id not in populated_db.libraries
    
    assert sample_document.id not in populated_db.documents
    assert sample_document.id not in populated_db.document_library_map
    assert sample_chunk.id not in populated_db.chunks
    assert sample_chunk.id not in populated_db.chunk_document_map

def test_delete_nonexistent_library(reset_db):
    result = delete_library(uuid4())
    
    assert result is False 