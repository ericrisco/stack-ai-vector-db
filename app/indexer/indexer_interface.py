from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.models.chunk import Chunk
from app.models.library import Library, IndexerType


class VectorIndexer(ABC):
    """
    Interface for vector indexers.
    Different indexing algorithms can implement this interface.
    """
    
    @abstractmethod
    async def index_library(self, library_id: UUID) -> Dict[str, Any]:
        """
        Index all documents and chunks in a library.
        
        Args:
            library_id: UUID of the library to index
            
        Returns:
            Dict containing indexing stats and information
        """
        pass
    
    @abstractmethod
    async def search(self, text: str, library_id: UUID, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for chunks similar to the provided text.
        
        Args:
            text: Text to search for
            library_id: Library ID to limit the search scope
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing search results
        """
        pass
    
    @abstractmethod
    def get_indexer_name(self) -> IndexerType:
        """
        Get the name of the indexer implementation
        
        Returns:
            IndexerType enum value for this indexer
        """
        pass
    
    @abstractmethod
    def get_indexer_info(self) -> Dict[str, Any]:
        """
        Get information about the indexer
        
        Returns:
            Dictionary with information about the indexer implementation
        """
        pass