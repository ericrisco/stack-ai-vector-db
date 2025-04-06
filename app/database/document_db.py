from typing import List, Optional, Dict
from uuid import UUID
from app.models.document import Document
from app.database.db import get_db
from app.database.chunk_db import create_chunk, delete_chunks_by_document, get_chunks_by_document
from app.database.persistence import save_library
import logging

logger = logging.getLogger(__name__)

def create_document(document: Document) -> Document:
    """
    Create a new document in the database
    """
    db = get_db()
    with db.document_lock:
        # Check if document with this ID already exists
        if document.id in db.documents:
            raise ValueError(f"Document with ID {document.id} already exists")
        
        # Check if the referenced library exists
        if document.library_id not in db.libraries:
            raise ValueError(f"Library with ID {document.library_id} does not exist")
        
        # Store the document
        db.documents[document.id] = document.model_dump()
        
        # Track the relationship
        db.document_library_map[document.id] = document.library_id
        
        # Ensure each chunk references this document and then store it
        for chunk in document.chunks:
            chunk.document_id = document.id
            try:
                create_chunk(chunk)
            except ValueError as e:
                # If there's an error, provide context
                raise ValueError(f"Error creating chunk: {str(e)}")
        
        # Save to persistent storage
        save_library(document.library_id)
        
        return document

def get_document(document_id: UUID) -> Optional[Document]:
    """
    Get a document by ID
    """
    db = get_db()
    with db.document_lock:
        document_data = db.documents.get(document_id)
        if not document_data:
            return None
        return Document(**document_data)

def get_all_documents() -> List[Document]:
    """
    Get all documents
    """
    db = get_db()
    with db.document_lock:
        return [Document(**doc_data) for doc_data in db.documents.values()]

def get_documents_by_library(library_id: UUID) -> List[Document]:
    """
    Get all documents belonging to a library, with their chunks
    """
    db = get_db()
    documents = []
    
    with db.document_lock:
        document_ids = [
            doc_id for doc_id, lib_id in db.document_library_map.items() 
            if lib_id == library_id and doc_id in db.documents
        ]
        
        for doc_id in document_ids:
            # Create the document without chunks initially
            document_data = db.documents[doc_id]
            document = Document(**document_data)
            
            # Get the chunks for this document
            document.chunks = get_chunks_by_document(doc_id)
            
            documents.append(document)
    
    return documents

def update_document(document_id: UUID, document_data: Dict) -> Optional[Document]:
    """
    Update an existing document
    """
    db = get_db()
    with db.document_lock:
        if document_id not in db.documents:
            return None
        
        # Get the current document data
        current_document = db.documents[document_id]
        
        # Cannot change library_id reference
        if "library_id" in document_data and str(document_data["library_id"]) != str(current_document["library_id"]):
            raise ValueError("Cannot change library_id of an existing document")
        
        # Don't allow updating chunks through this method
        if "chunks" in document_data:
            raise ValueError("Cannot update chunks through document update. Use chunk API instead.")
        
        # Update the document data
        current_document.update(document_data)
        
        # Validate using the model
        updated_document = Document(**current_document)
        
        # Store back to the database
        db.documents[document_id] = updated_document.model_dump()
        
        # Save to persistent storage
        library_id = db.document_library_map.get(document_id)
        if library_id:
            save_library(library_id)
        
        return updated_document

def delete_document(document_id: UUID) -> bool:
    """
    Delete a document by ID, also deleting all its chunks
    """
    db = get_db()
    
    # Get library_id before deletion for persistence
    library_id = None
    with db.document_lock:
        if document_id in db.document_library_map:
            library_id = db.document_library_map[document_id]
    
    with db.document_lock:
        if document_id not in db.documents:
            return False
        
        # Delete all chunks associated with the document
        delete_chunks_by_document(document_id)
        
        # Remove the document
        del db.documents[document_id]
        
        # Remove the relationship
        if document_id in db.document_library_map:
            del db.document_library_map[document_id]
        
        # Save to persistent storage
        if library_id:
            save_library(library_id)
        
        return True

def delete_documents_by_library(library_id: UUID) -> int:
    """
    Delete all documents associated with a library
    Returns the number of documents deleted
    """
    db = get_db()
    with db.document_lock:
        # Find all documents belonging to this library
        document_ids = [
            doc_id for doc_id, lib_id in db.document_library_map.items() 
            if lib_id == library_id
        ]
        
        # Delete each document and its chunks
        count = 0
        for doc_id in document_ids:
            if delete_document(doc_id):
                count += 1
        
        return count 