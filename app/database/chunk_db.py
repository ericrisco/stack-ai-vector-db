from typing import List, Optional, Dict
from uuid import UUID
from app.models.chunk import Chunk
from app.database.db import get_db
from app.database.persistence import save_library
import logging

logger = logging.getLogger(__name__)

def create_chunk(chunk: Chunk) -> Chunk:
    """
    Create a new chunk in the database
    """
    db = get_db()
    
    # Track the document and library for persistence
    document_id = chunk.document_id
    library_id = None
    
    if document_id:
        with db.document_lock:
            if document_id in db.document_library_map:
                library_id = db.document_library_map[document_id]
    
    with db.chunk_lock:
        # Check if chunk with this ID already exists
        if chunk.id in db.chunks:
            raise ValueError(f"Chunk with ID {chunk.id} already exists")
        
        # Check if the referenced document exists
        if chunk.document_id is not None and chunk.document_id not in db.documents:
            raise ValueError(f"Document with ID {chunk.document_id} does not exist")
        
        # Store the chunk
        db.chunks[chunk.id] = chunk.model_dump()
        
        # Track the relationship if document_id is provided
        if chunk.document_id is not None:
            db.chunk_document_map[chunk.id] = chunk.document_id
    
    # Save to persistent storage
    if library_id:
        save_library(library_id)
        
    return chunk

def get_chunk(chunk_id: UUID) -> Optional[Chunk]:
    """
    Get a chunk by ID
    """
    db = get_db()
    with db.chunk_lock:
        chunk_data = db.chunks.get(chunk_id)
        if not chunk_data:
            return None
        return Chunk(**chunk_data)

def get_all_chunks() -> List[Chunk]:
    """
    Get all chunks
    """
    db = get_db()
    with db.chunk_lock:
        return [Chunk(**chunk_data) for chunk_data in db.chunks.values()]

def get_chunks_by_document(document_id: UUID) -> List[Chunk]:
    """
    Get all chunks belonging to a document
    """
    db = get_db()
    with db.chunk_lock:
        return [
            Chunk(**db.chunks[chunk_id]) 
            for chunk_id, doc_id in db.chunk_document_map.items() 
            if doc_id == document_id and chunk_id in db.chunks
        ]

def update_chunk(chunk_id: UUID, chunk_data: Dict) -> Optional[Chunk]:
    """
    Update an existing chunk
    """
    db = get_db()
    
    # Track the document and library for persistence
    document_id = None
    library_id = None
    
    with db.chunk_lock:
        if chunk_id in db.chunk_document_map:
            document_id = db.chunk_document_map[chunk_id]
    
    if document_id:
        with db.document_lock:
            if document_id in db.document_library_map:
                library_id = db.document_library_map[document_id]
    
    with db.chunk_lock:
        if chunk_id not in db.chunks:
            return None
        
        # Get the current chunk data
        current_chunk = db.chunks[chunk_id]
        
        # Cannot change document_id reference
        if "document_id" in chunk_data and str(chunk_data["document_id"]) != str(current_chunk["document_id"]):
            raise ValueError("Cannot change document_id of an existing chunk")
        
        # Update the chunk data
        current_chunk.update(chunk_data)
        
        # Validate using the model
        updated_chunk = Chunk(**current_chunk)
        
        # Store back to the database
        db.chunks[chunk_id] = updated_chunk.model_dump()
    
    # Save to persistent storage
    if library_id:
        save_library(library_id)
        
    return updated_chunk

def delete_chunk(chunk_id: UUID) -> bool:
    """
    Delete a chunk by ID
    """
    db = get_db()
    
    # Track the document and library for persistence
    document_id = None
    library_id = None
    
    with db.chunk_lock:
        if chunk_id in db.chunk_document_map:
            document_id = db.chunk_document_map[chunk_id]
    
    if document_id:
        with db.document_lock:
            if document_id in db.document_library_map:
                library_id = db.document_library_map[document_id]
    
    with db.chunk_lock:
        if chunk_id not in db.chunks:
            return False
        
        # Remove the chunk
        del db.chunks[chunk_id]
        
        # Remove the relationship
        if chunk_id in db.chunk_document_map:
            del db.chunk_document_map[chunk_id]
    
    # Save to persistent storage
    if library_id:
        save_library(library_id)
            
    return True

def delete_chunks_by_document(document_id: UUID) -> int:
    """
    Delete all chunks associated with a document
    Returns the number of chunks deleted
    """
    db = get_db()
    
    # Track the library for persistence
    library_id = None
    
    with db.document_lock:
        if document_id in db.document_library_map:
            library_id = db.document_library_map[document_id]
    
    with db.chunk_lock:
        # Find all chunks belonging to this document
        chunk_ids = [
            chunk_id for chunk_id, doc_id in db.chunk_document_map.items() 
            if doc_id == document_id
        ]
        
        # Delete each chunk
        for chunk_id in chunk_ids:
            if chunk_id in db.chunks:
                del db.chunks[chunk_id]
            
            # Remove relationship
            del db.chunk_document_map[chunk_id]
        
        # Save to persistent storage
        if library_id and chunk_ids:
            save_library(library_id)
        
        return len(chunk_ids) 