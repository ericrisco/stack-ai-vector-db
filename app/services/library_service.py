from typing import List, Optional, Dict, Any
from uuid import UUID
import time
import asyncio
from app.models.library import Library, IndexStatus, IndexerType
from app.database import (
    create_library,
    get_library,
    get_all_libraries,
    update_library,
    delete_library
)
from app.indexer.indexer_interface import VectorIndexer

# Global dictionary to store indexers for libraries
library_indexers = {}
# Global set to track libraries that are currently being indexed
indexing_tasks = {}

class LibraryService:
    @staticmethod
    def create_library(library: Library) -> Library:
        """
        Create a new library with its documents and chunks
        """
        # Initialize with not indexed status
        library.index_status = IndexStatus()
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
        
        # If a library is being indexed, don't allow certain updates
        library = get_library(library_id)
        if library and library.index_status.indexing_in_progress:
            raise ValueError("Cannot update library while indexing is in progress")
        
        return update_library(library_id, library_data)
    
    @staticmethod
    def delete_library(library_id: UUID) -> bool:
        """
        Delete a library and all its documents and chunks (cascade delete)
        """
        # Remove any indexers for this library
        if library_id in library_indexers:
            del library_indexers[library_id]
        
        # Cancel any indexing tasks
        if library_id in indexing_tasks:
            # The task might already be done, so we need to be careful
            task = indexing_tasks[library_id]
            if not task.done():
                task.cancel()
            del indexing_tasks[library_id]
        
        return delete_library(library_id)
    
    @staticmethod
    def mark_library_unindexed(library_id: UUID) -> bool:
        """
        Mark a library as no longer fully indexed
        This should be called when documents or chunks are added/removed
        """
        library = get_library(library_id)
        if not library:
            return False
        
        # Only update if the library was previously indexed
        if library.index_status.indexed:
            # Update status to not indexed but preserve the indexer type
            update_data = {
                "index_status": {
                    "indexed": False,
                    "indexer_type": library.index_status.indexer_type,
                    "last_indexed": library.index_status.last_indexed,
                    "indexing_in_progress": False
                }
            }
            update_library(library_id, update_data)
        
        return True
    
    @staticmethod
    def get_indexer_for_library(library_id: UUID) -> Optional[VectorIndexer]:
        """
        Get the indexer instance for a library if it exists
        """
        return library_indexers.get(library_id)
    
    @staticmethod
    async def start_indexing_library(
        library_id: UUID, 
        indexer_type: IndexerType,
        leaf_size: int = 40
    ) -> Dict[str, Any]:
        """
        Start indexing a library asynchronously
        
        Args:
            library_id: UUID of the library to index
            indexer_type: Type of indexer to use
            leaf_size: Size of leaf nodes for Ball Tree indexer
            
        Returns:
            Dictionary with status information
        """
        library = get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        
        # Check if already being indexed
        if library.index_status.indexing_in_progress:
            return {"status": "indexing_in_progress", "message": "Library is already being indexed"}
        
        # Mark as indexing in progress
        update_data = {
            "index_status": {
                "indexed": False,
                "indexer_type": indexer_type,
                "last_indexed": None,
                "indexing_in_progress": True
            }
        }
        update_library(library_id, update_data)
        
        # Import dynamically to avoid circular imports
        from app.indexer import create_indexer
        
        # Create the appropriate indexer
        if indexer_type == IndexerType.BALL_TREE:
            indexer = create_indexer(indexer_type, leaf_size=leaf_size)
        else:
            indexer = create_indexer(indexer_type)
        
        # Store the indexer
        library_indexers[library_id] = indexer
        
        # Start indexing in a background task
        task = asyncio.create_task(LibraryService._index_library_task(library_id, indexer))
        indexing_tasks[library_id] = task
        
        return {
            "status": "indexing_started",
            "library_id": str(library_id),
            "indexer_type": indexer_type
        }
    
    @staticmethod
    async def _index_library_task(library_id: UUID, indexer: VectorIndexer) -> None:
        """
        Background task to index a library
        """
        try:
            # Perform the indexing operation
            stats = await indexer.index_library(library_id)
            
            # Update the library status
            update_data = {
                "index_status": {
                    "indexed": True,
                    "indexer_type": indexer.get_indexer_name(),
                    "last_indexed": time.time(),
                    "indexing_in_progress": False
                }
            }
            update_library(library_id, update_data)
            
            print(f"Indexing completed for library {library_id}")
            print(f"Stats: {stats}")
            
        except Exception as e:
            print(f"Error indexing library {library_id}: {str(e)}")
            
            # Update the library status to indicate failure
            update_data = {
                "index_status": {
                    "indexed": False,
                    "indexer_type": None,
                    "last_indexed": None,
                    "indexing_in_progress": False
                }
            }
            update_library(library_id, update_data)
            
            # Remove the indexer
            if library_id in library_indexers:
                del library_indexers[library_id]
        
        finally:
            # Clean up the task
            if library_id in indexing_tasks:
                del indexing_tasks[library_id]
    
    @staticmethod
    async def search_library(
        library_id: UUID, 
        query_text: str, 
        top_k: int = 5
    ) -> List["SearchResult"]:
        """
        Search for similar content in a library
        
        Args:
            library_id: UUID of the library to search
            query_text: Text to search for
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        from app.services.document_service import DocumentService
        from app.models.search import SearchResult, DocumentInfo
        
        library = get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        
        # Check if the library is indexed
        if not library.index_status.indexed:
            if library.index_status.indexing_in_progress:
                raise ValueError(f"Library is currently being indexed. Please try again later.")
            else:
                raise ValueError(f"Library is not indexed. Please index the library before searching.")
        
        # Get the indexer
        indexer = library_indexers.get(library_id)
        if not indexer:
            raise ValueError(f"No indexer found for library. Please re-index the library.")
        
        # Perform the search
        raw_results = await indexer.search(query_text, library_id, top_k)
        
        # Format results using Pydantic models
        results = []
        for result in raw_results:
            # Get the complete document - use string version of UUID for lookup
            document_id = result["document_id"]
            # Convert to UUID object if it's a string
            if isinstance(document_id, str):
                document_id = UUID(document_id)
            
            document = DocumentService.get_document(document_id)
            
            # Create DocumentInfo model
            doc_info = None
            if document:
                doc_info = DocumentInfo(
                    id=str(document.id),
                    name=document.name,
                    metadata=document.metadata
                )
            else:
                # If document not found, create minimal info
                doc_info = DocumentInfo(
                    id=str(document_id),
                    name="Unknown Document",
                    metadata={}
                )
            
            # Convert UUID to string if needed
            chunk_id = result["chunk_id"]
            if isinstance(chunk_id, UUID):
                chunk_id = str(chunk_id)
            
            # Create a SearchResult model instance
            search_result = SearchResult(
                chunk_id=chunk_id,
                text=result["text"],
                score=result["similarity_score"],
                document=doc_info,
            )
            
            results.append(search_result)
            
        return results
    
    @staticmethod
    def get_indexing_status(library_id: UUID) -> Dict[str, Any]:
        """
        Get the current indexing status of a library
        
        Args:
            library_id: UUID of the library to check
            
        Returns:
            Dictionary with status information
        """
        library = get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        
        status = {
            "library_id": str(library_id),
            "indexed": library.index_status.indexed,
            "indexer_type": library.index_status.indexer_type,
            "indexing_in_progress": library.index_status.indexing_in_progress
        }
        
        if library.index_status.last_indexed:
            status["last_indexed"] = library.index_status.last_indexed
        
        # Add information about the indexer if available
        indexer = library_indexers.get(library_id)
        if indexer:
            status["indexer_info"] = indexer.get_indexer_info()
        
        return status 