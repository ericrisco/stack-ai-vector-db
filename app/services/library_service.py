from typing import List, Optional, Dict
from uuid import UUID
from app.models.library import Library
from app.database import (
    create_library,
    get_library,
    get_all_libraries,
    update_library,
    delete_library
)

class LibraryService:
    @staticmethod
    def create_library(library: Library) -> Library:
        """
        Create a new library with its documents and chunks
        """
        return create_library(library)
    
    @staticmethod
    def get_library(library_id: UUID) -> Optional[Library]:
        """
        Get a library by ID
        """
        return get_library(library_id)
    
    @staticmethod
    def get_all_libraries() -> List[Library]:
        """
        Get all libraries
        """
        return get_all_libraries()
    
    @staticmethod
    def update_library(library_id: UUID, library_data: Dict) -> Optional[Library]:
        """
        Update library information (excluding documents and chunks)
        """
        # Ensure documents cannot be updated directly
        if "documents" in library_data:
            raise ValueError("Cannot update documents through library update. Use document service instead.")
        
        return update_library(library_id, library_data)
    
    @staticmethod
    def delete_library(library_id: UUID) -> bool:
        """
        Delete a library and all its documents and chunks (cascade delete)
        """
        return delete_library(library_id) 