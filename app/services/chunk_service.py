from typing import List, Optional, Dict
from uuid import UUID
from app.models.chunk import Chunk
from app.database import (
    create_chunk,
    get_chunk,
    get_all_chunks,
    get_chunks_by_document,
    update_chunk,
    delete_chunk,
    get_document
)

class ChunkService:
    @staticmethod
    def create_chunk(chunk: Chunk) -> Chunk:
        """
        Create a single chunk for a document
        """
        # Verify that the document exists before creating the chunk
        document = get_document(chunk.document_id)
        if not document:
            raise ValueError(f"Document with ID {chunk.document_id} does not exist")
        
        # Create the chunk
        created_chunk = create_chunk(chunk)
        
        # Import inside method to avoid circular imports
        from app.services.library_service import LibraryService
        
        # Mark the library as not indexed if the document belongs to a library
        if document.library_id:
            LibraryService.mark_library_unindexed(document.library_id)
        
        return created_chunk
    
    @staticmethod
    def create_chunks(chunks: List[Chunk]) -> List[Chunk]:
        """
        Create multiple chunks for a document
        """
        # Ensure all chunks reference the same document
        if not chunks:
            return []
        
        document_id = chunks[0].document_id
        for chunk in chunks:
            if chunk.document_id != document_id:
                raise ValueError("All chunks must belong to the same document")
        
        # Verify that the document exists
        document = get_document(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} does not exist")
        
        # Create all chunks
        created_chunks = []
        for chunk in chunks:
            created_chunks.append(create_chunk(chunk))
        
        # Import inside method to avoid circular imports
        from app.services.library_service import LibraryService
        
        # Mark the library as not indexed if the document belongs to a library
        if document.library_id:
            LibraryService.mark_library_unindexed(document.library_id)
        
        return created_chunks
    
    @staticmethod
    def get_chunk(chunk_id: UUID) -> Optional[Chunk]:
        """
        Get a chunk by ID
        """
        return get_chunk(chunk_id)
    
    @staticmethod
    def get_all_chunks() -> List[Chunk]:
        """
        Get all chunks
        """
        return get_all_chunks()
    
    @staticmethod
    def get_chunks_by_document(document_id: UUID) -> List[Chunk]:
        """
        Get all chunks belonging to a document
        """
        return get_chunks_by_document(document_id)
    
    @staticmethod
    def update_chunk(chunk_id: UUID, chunk_data: Dict) -> Optional[Chunk]:
        """
        Update an existing chunk
        """
        # Get the chunk and document to determine the library
        chunk = get_chunk(chunk_id)
        if not chunk:
            return None
            
        document = get_document(chunk.document_id)
        if not document:
            return None
            
        # Update the chunk
        updated_chunk = update_chunk(chunk_id, chunk_data)
        
        # Import inside method to avoid circular imports
        from app.services.library_service import LibraryService
        
        # Mark the library as not indexed if the document belongs to a library
        if document.library_id:
            LibraryService.mark_library_unindexed(document.library_id)
            
        return updated_chunk
    
    @staticmethod
    def delete_chunk(chunk_id: UUID) -> bool:
        """
        Delete a chunk
        """
        # Get the chunk and document to determine the library
        chunk = get_chunk(chunk_id)
        if not chunk:
            return False
            
        document = get_document(chunk.document_id)
        if not document:
            return False
            
        # Delete the chunk
        result = delete_chunk(chunk_id)
        
        # If deletion was successful and the document belongs to a library, mark it as not indexed
        if result and document.library_id:
            # Import inside method to avoid circular imports
            from app.services.library_service import LibraryService
            LibraryService.mark_library_unindexed(document.library_id)
            
        return result 