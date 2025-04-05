from typing import List, Optional, Dict
from uuid import UUID
from app.models.library import Library
from app.database.db import get_db
from app.database.document_db import create_document, delete_documents_by_library

def create_library(library: Library) -> Library:
    """
    Create a new library in the database
    """
    db = get_db()
    with db.library_lock:
        # Check if library with this ID already exists
        if library.id in db.libraries:
            raise ValueError(f"Library with ID {library.id} already exists")
        
        # Ensure each document references this library
        for document in library.documents:
            document.library_id = library.id
        
        # Store the library
        db.libraries[library.id] = library.model_dump()
        
        # Store associated documents
        for document in library.documents:
            try:
                create_document(document)
            except ValueError as e:
                # If there's an error, provide context
                raise ValueError(f"Error creating document: {str(e)}")
        
        return library

def get_library(library_id: UUID) -> Optional[Library]:
    """
    Get a library by ID
    """
    db = get_db()
    with db.library_lock:
        library_data = db.libraries.get(library_id)
        if not library_data:
            return None
        return Library(**library_data)

def get_all_libraries() -> List[Library]:
    """
    Get all libraries
    """
    db = get_db()
    with db.library_lock:
        return [Library(**library_data) for library_data in db.libraries.values()]

def update_library(library_id: UUID, library_data: Dict) -> Optional[Library]:
    """
    Update an existing library
    """
    db = get_db()
    with db.library_lock:
        if library_id not in db.libraries:
            return None
        
        # Get the current library data
        current_library = db.libraries[library_id]
        
        # Don't allow updating documents through this method
        if "documents" in library_data:
            raise ValueError("Cannot update documents through library update. Use document API instead.")
        
        # Update the library data
        current_library.update(library_data)
        
        # Validate using the model
        updated_library = Library(**current_library)
        
        # Store back to the database
        db.libraries[library_id] = updated_library.model_dump()
        
        return updated_library

def delete_library(library_id: UUID) -> bool:
    """
    Delete a library by ID, also deleting all its documents and chunks
    """
    db = get_db()
    with db.library_lock:
        if library_id not in db.libraries:
            return False
        
        # Delete all documents (and their chunks) associated with the library
        delete_documents_by_library(library_id)
        
        # Delete the library
        del db.libraries[library_id]
        
        return True 