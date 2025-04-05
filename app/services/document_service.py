from typing import List, Optional, Dict
from uuid import UUID
from app.models.document import Document
from app.models.chunk import Chunk
from app.database import (
    create_document,
    get_document,
    get_all_documents,
    get_documents_by_library,
    update_document,
    delete_document,
    get_db,
    create_chunk,
    delete_chunks_by_document
)

class DocumentService:
    @staticmethod
    def create_document(document: Document) -> Document:
        """
        Create a single document with its chunks
        """
        return create_document(document)
    
    @staticmethod
    def create_documents(documents: List[Document]) -> List[Document]:
        """
        Create multiple documents at once
        """
        created_documents = []
        for document in documents:
            created_documents.append(create_document(document))
        return created_documents
    
    @staticmethod
    def get_document(document_id: UUID) -> Optional[Document]:
        """
        Get a document by ID
        """
        return get_document(document_id)
    
    @staticmethod
    def get_all_documents() -> List[Document]:
        """
        Get all documents
        """
        return get_all_documents()
    
    @staticmethod
    def get_documents_by_library(library_id: UUID) -> List[Document]:
        """
        Get all documents in a library
        """
        return get_documents_by_library(library_id)
    
    @staticmethod
    def update_document(document_id: UUID, document_data: Dict) -> Optional[Document]:
        """
        Update document information (excluding chunks)
        """
        # Cannot update chunks directly through this method
        if "chunks" in document_data:
            raise ValueError("Cannot update chunks through this method. Use update_document_chunks instead.")
        
        return update_document(document_id, document_data)
    
    @staticmethod
    def update_document_chunks(document_id: UUID, chunks: List[Chunk]) -> Optional[Document]:
        """
        Replace all chunks of a document with new ones
        """
        # Get the document first to check if it exists
        document = get_document(document_id)
        if not document:
            return None
        
        db = get_db()
        
        # Using document_lock to ensure atomicity
        with db.document_lock:
            # Delete all existing chunks
            delete_chunks_by_document(document_id)
            
            # Set document_id for all new chunks
            for chunk in chunks:
                chunk.document_id = document_id
                
            # Create new chunks
            for chunk in chunks:
                create_chunk(chunk)
            
            # Update the document in memory with new chunks
            document.chunks = chunks
            
            # Update the document in database
            document_data = document.model_dump()
            db.documents[document_id] = document_data
            
            return document
    
    @staticmethod
    def delete_document(document_id: UUID) -> bool:
        """
        Delete a document and all its chunks (cascade delete)
        """
        return delete_document(document_id) 