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
        if not get_document(chunk.document_id):
            raise ValueError(f"Document with ID {chunk.document_id} does not exist")
        
        return create_chunk(chunk)
    
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
        if not get_document(document_id):
            raise ValueError(f"Document with ID {document_id} does not exist")
        
        # Create all chunks
        created_chunks = []
        for chunk in chunks:
            created_chunks.append(create_chunk(chunk))
        
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
        return update_chunk(chunk_id, chunk_data)
    
    @staticmethod
    def delete_chunk(chunk_id: UUID) -> bool:
        """
        Delete a chunk
        """
        return delete_chunk(chunk_id) 