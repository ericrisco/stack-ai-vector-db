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
        # Create the document
        created_doc = create_document(document)
        
        # Import inside method to avoid circular imports
        from app.services.library_service import LibraryService
        
        # Mark library as not indexed
        if created_doc.library_id:
            LibraryService.mark_library_unindexed(created_doc.library_id)
            
        return created_doc
    
    @staticmethod
    def create_documents(documents: List[Document]) -> List[Document]:
        """
        Create multiple documents at once
        """
        created_documents = []
        
        # Import inside method to avoid circular imports
        from app.services.library_service import LibraryService
        
        # Track unique library IDs to mark them unindexed only once
        library_ids = set()
        
        for document in documents:
            created_doc = create_document(document)
            created_documents.append(created_doc)
            
            if created_doc.library_id:
                library_ids.add(created_doc.library_id)
        
        # Mark all affected libraries as not indexed
        for library_id in library_ids:
            LibraryService.mark_library_unindexed(library_id)
            
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
        
        # Get the document first to check if it exists and to get the library_id
        document = get_document(document_id)
        if not document:
            return None
            
        # Update the document
        updated_doc = update_document(document_id, document_data)
        
        # If library_id changed, mark both old and new libraries as not indexed
        if "library_id" in document_data and document_data["library_id"] != document.library_id:
            # Import inside method to avoid circular imports
            from app.services.library_service import LibraryService
            
            # Mark old library as not indexed
            if document.library_id:
                LibraryService.mark_library_unindexed(document.library_id)
                
            # Mark new library as not indexed
            if document_data["library_id"]:
                LibraryService.mark_library_unindexed(document_data["library_id"])
        
        return updated_doc
    
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
            
            # Import inside method to avoid circular imports
            from app.services.library_service import LibraryService
            
            # Mark library as not indexed
            if document.library_id:
                LibraryService.mark_library_unindexed(document.library_id)
            
            return document
    
    @staticmethod
    def delete_document(document_id: UUID) -> bool:
        """
        Delete a document and all its chunks (cascade delete)
        """
        # Get the document first to get the library_id
        document = get_document(document_id)
        
        # Delete the document
        result = delete_document(document_id)
        
        # If deletion was successful and we have a library_id, mark it as not indexed
        if result and document and document.library_id:
            # Import inside method to avoid circular imports
            from app.services.library_service import LibraryService
            LibraryService.mark_library_unindexed(document.library_id)
        
        return result 