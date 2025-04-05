import pytest
import threading
from uuid import UUID, uuid4
from app.database.db import DB, get_db
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library

@pytest.fixture(scope="function")
def reset_db():
    db = get_db()
    
    # Ensure all locks are released
    if hasattr(db.library_lock, "_is_owned") and db.library_lock._is_owned():
        db.library_lock.release()
    if hasattr(db.document_lock, "_is_owned") and db.document_lock._is_owned():
        db.document_lock.release()
    if hasattr(db.chunk_lock, "_is_owned") and db.chunk_lock._is_owned():
        db.chunk_lock.release()
    
    # Clear all data
    db.libraries.clear()
    db.documents.clear()
    db.chunks.clear()
    db.document_library_map.clear()
    db.chunk_document_map.clear()
    
    yield db
    
    # Ensure all locks are released again
    if hasattr(db.library_lock, "_is_owned") and db.library_lock._is_owned():
        db.library_lock.release()
    if hasattr(db.document_lock, "_is_owned") and db.document_lock._is_owned():
        db.document_lock.release()
    if hasattr(db.chunk_lock, "_is_owned") and db.chunk_lock._is_owned():
        db.chunk_lock.release()
    
    # Clean up after test
    db.libraries.clear()
    db.documents.clear()
    db.chunks.clear()
    db.document_library_map.clear()
    db.chunk_document_map.clear()

@pytest.fixture
def sample_library_id():
    return uuid4()

@pytest.fixture
def sample_document_id():
    return uuid4()

@pytest.fixture
def sample_chunk_id():
    return uuid4()

@pytest.fixture
def sample_library(sample_library_id):
    return Library(
        id=sample_library_id,
        name="Test Library",
        documents=[],
        metadata={"key": "value"}
    )

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
def sample_chunk(sample_chunk_id, sample_document_id):
    return Chunk(
        id=sample_chunk_id,
        document_id=sample_document_id,
        text="This is a test chunk",
        embedding=[0.1, 0.2, 0.3, 0.4],
        metadata={"key": "value"}
    )

@pytest.fixture
def populated_db(reset_db, sample_library, sample_document, sample_chunk):
    db = reset_db
    
    # Create a library
    db.libraries[sample_library.id] = sample_library.model_dump()
    
    # Create a document
    db.documents[sample_document.id] = sample_document.model_dump()
    db.document_library_map[sample_document.id] = sample_library.id
    
    # Create a chunk
    db.chunks[sample_chunk.id] = sample_chunk.model_dump()
    db.chunk_document_map[sample_chunk.id] = sample_document.id
    
    return db 