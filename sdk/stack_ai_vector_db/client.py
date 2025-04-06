import requests
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from .models.library import Library, IndexerType
from .models.document import Document
from .models.chunk import Chunk
from .models.search import SearchResult
from .exceptions import APIError, NotFoundError, ValidationError, IndexingError


class VectorDBClient:
    """
    Client for the Stack AI Vector Database API.
    
    This client provides methods to interact with all aspects of the Vector DB,
    including managing libraries, documents, and chunks, as well as searching for similar content.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize the Vector DB client.
        
        Args:
            base_url: The base URL of the Vector DB API (default: "http://localhost:8000")
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        
        # Configure headers if api_key is provided
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    # === Libraries ===
    
    def create_library(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Library:
        """
        Create a new library.
        
        Args:
            name: The name of the library
            metadata: Optional metadata for the library
            
        Returns:
            Library: The created library object
            
        Raises:
            ValidationError: If validation fails
            APIError: If the API request fails
        """
        payload = {"name": name, "metadata": metadata or {}}
        response = self._post("/api/libraries", json=payload)
        return Library(**response)
    
    def get_libraries(self) -> List[Library]:
        """
        Get all libraries.
        
        Returns:
            List[Library]: List of all libraries
            
        Raises:
            APIError: If the API request fails
        """
        response = self._get("/api/libraries")
        return [Library(**lib) for lib in response]
    
    def get_library(self, library_id: Union[str, UUID]) -> Library:
        """
        Get a specific library by ID.
        
        Args:
            library_id: The ID of the library to retrieve
            
        Returns:
            Library: The requested library
            
        Raises:
            NotFoundError: If the library is not found
            APIError: If the API request fails
        """
        response = self._get(f"/api/libraries/{library_id}")
        return Library(**response)
    
    def update_library(self, library_id: Union[str, UUID], 
                      data: Dict[str, Any]) -> Library:
        """
        Update a library.
        
        Args:
            library_id: The ID of the library to update
            data: Dictionary with fields to update
            
        Returns:
            Library: The updated library
            
        Raises:
            NotFoundError: If the library is not found
            ValidationError: If validation fails
            APIError: If the API request fails
        """
        response = self._patch(f"/api/libraries/{library_id}", json=data)
        return Library(**response)
    
    def delete_library(self, library_id: Union[str, UUID]) -> bool:
        """
        Delete a library.
        
        Args:
            library_id: The ID of the library to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            NotFoundError: If the library is not found
            APIError: If the API request fails
        """
        self._delete(f"/api/libraries/{library_id}")
        return True
    
    def index_library(self, library_id: Union[str, UUID], 
                     indexer_type: Union[str, IndexerType] = "BRUTE_FORCE",
                     leaf_size: int = 40) -> Dict[str, Any]:
        """
        Start indexing a library.
        
        Args:
            library_id: The ID of the library to index
            indexer_type: Type of indexer to use (BRUTE_FORCE or BALL_TREE)
            leaf_size: Leaf size for Ball Tree indexer (default: 40)
            
        Returns:
            Dict[str, Any]: Indexing status information
            
        Raises:
            NotFoundError: If the library is not found
            ValidationError: If validation fails
            IndexingError: If indexing fails
            APIError: If the API request fails
        """
        if isinstance(indexer_type, IndexerType):
            indexer_type = indexer_type.value
            
        payload = {"indexer_type": indexer_type, "leaf_size": leaf_size}
        return self._post(f"/api/libraries/{library_id}/index", json=payload)
    
    def get_indexing_status(self, library_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Get indexing status of a library.
        
        Args:
            library_id: The ID of the library
            
        Returns:
            Dict[str, Any]: Indexing status information
            
        Raises:
            NotFoundError: If the library is not found
            APIError: If the API request fails
        """
        return self._get(f"/api/libraries/{library_id}/index/status")
    
    def search(self, library_id: Union[str, UUID], 
              query_text: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search for similar content in the library.
        
        Args:
            library_id: The ID of the library to search
            query_text: The text to search for
            top_k: Number of results to return (default: 5)
            
        Returns:
            List[SearchResult]: List of search results
            
        Raises:
            NotFoundError: If the library is not found
            ValidationError: If the library is not indexed
            APIError: If the API request fails
        """
        params = {"query_text": query_text, "top_k": top_k}
        response = self._post(f"/api/libraries/{library_id}/search", params=params)
        return [SearchResult(**result) for result in response]
    
    # === Documents ===
    
    def create_document(self, library_id: Union[str, UUID], 
                       name: str, chunks: List[Dict] = None,
                       metadata: Dict[str, Any] = None) -> Document:
        """
        Create a new document with optional chunks.
        
        Args:
            library_id: The ID of the library this document belongs to
            name: The name of the document
            chunks: Optional list of chunks to create with the document
            metadata: Optional metadata for the document
            
        Returns:
            Document: The created document
            
        Raises:
            ValidationError: If validation fails
            NotFoundError: If the library is not found
            APIError: If the API request fails
        """
        payload = {
            "library_id": str(library_id),
            "name": name,
            "metadata": metadata or {},
            "chunks": chunks or []
        }
        response = self._post("/api/documents", json=payload)
        return Document(**response)
    
    def get_documents(self) -> List[Document]:
        """
        Get all documents.
        
        Returns:
            List[Document]: List of all documents
            
        Raises:
            APIError: If the API request fails
        """
        response = self._get("/api/documents")
        return [Document(**doc) for doc in response]
    
    def get_document(self, document_id: Union[str, UUID]) -> Document:
        """
        Get a specific document.
        
        Args:
            document_id: The ID of the document to retrieve
            
        Returns:
            Document: The requested document
            
        Raises:
            NotFoundError: If the document is not found
            APIError: If the API request fails
        """
        response = self._get(f"/api/documents/{document_id}")
        return Document(**response)
    
    def get_documents_by_library(self, library_id: Union[str, UUID]) -> List[Document]:
        """
        Get all documents in a library.
        
        Args:
            library_id: The ID of the library
            
        Returns:
            List[Document]: List of documents in the library
            
        Raises:
            APIError: If the API request fails
        """
        response = self._get(f"/api/documents/library/{library_id}")
        return [Document(**doc) for doc in response]
    
    def update_document(self, document_id: Union[str, UUID], 
                       data: Dict[str, Any]) -> Document:
        """
        Update a document.
        
        Args:
            document_id: The ID of the document to update
            data: Dictionary with fields to update
            
        Returns:
            Document: The updated document
            
        Raises:
            NotFoundError: If the document is not found
            ValidationError: If validation fails
            APIError: If the API request fails
        """
        response = self._patch(f"/api/documents/{document_id}", json=data)
        return Document(**response)
    
    def delete_document(self, document_id: Union[str, UUID]) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: The ID of the document to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            NotFoundError: If the document is not found
            APIError: If the API request fails
        """
        self._delete(f"/api/documents/{document_id}")
        return True
    
    # === Chunks ===
    
    def create_chunk(self, document_id: Union[str, UUID], 
                    text: str, metadata: Dict[str, Any] = None) -> Chunk:
        """
        Create a new chunk.
        
        Args:
            document_id: The ID of the document this chunk belongs to
            text: The text content of the chunk
            metadata: Optional metadata for the chunk
            
        Returns:
            Chunk: The created chunk
            
        Raises:
            ValidationError: If validation fails
            NotFoundError: If the document is not found
            APIError: If the API request fails
        """
        payload = {
            "document_id": str(document_id),
            "text": text,
            "metadata": metadata or {}
        }
        response = self._post("/api/chunks", json=payload)
        return Chunk(**response)
    
    def create_chunks(self, chunks: List[Dict]) -> List[Chunk]:
        """
        Create multiple chunks at once.
        
        Args:
            chunks: List of chunk data dictionaries
            
        Returns:
            List[Chunk]: List of created chunks
            
        Raises:
            ValidationError: If validation fails
            APIError: If the API request fails
        """
        response = self._post("/api/chunks/batch", json=chunks)
        return [Chunk(**chunk) for chunk in response]
    
    def get_chunks(self) -> List[Chunk]:
        """
        Get all chunks.
        
        Returns:
            List[Chunk]: List of all chunks
            
        Raises:
            APIError: If the API request fails
        """
        response = self._get("/api/chunks")
        return [Chunk(**chunk) for chunk in response]
    
    def get_chunk(self, chunk_id: Union[str, UUID]) -> Chunk:
        """
        Get a specific chunk.
        
        Args:
            chunk_id: The ID of the chunk to retrieve
            
        Returns:
            Chunk: The requested chunk
            
        Raises:
            NotFoundError: If the chunk is not found
            APIError: If the API request fails
        """
        response = self._get(f"/api/chunks/{chunk_id}")
        return Chunk(**response)
    
    def get_chunks_by_document(self, document_id: Union[str, UUID]) -> List[Chunk]:
        """
        Get all chunks in a document.
        
        Args:
            document_id: The ID of the document
            
        Returns:
            List[Chunk]: List of chunks in the document
            
        Raises:
            APIError: If the API request fails
        """
        response = self._get(f"/api/chunks/document/{document_id}")
        return [Chunk(**chunk) for chunk in response]
    
    def update_chunk(self, chunk_id: Union[str, UUID], 
                    data: Dict[str, Any]) -> Chunk:
        """
        Update a chunk.
        
        Args:
            chunk_id: The ID of the chunk to update
            data: Dictionary with fields to update
            
        Returns:
            Chunk: The updated chunk
            
        Raises:
            NotFoundError: If the chunk is not found
            ValidationError: If validation fails
            APIError: If the API request fails
        """
        response = self._patch(f"/api/chunks/{chunk_id}", json=data)
        return Chunk(**response)
    
    def delete_chunk(self, chunk_id: Union[str, UUID]) -> bool:
        """
        Delete a chunk.
        
        Args:
            chunk_id: The ID of the chunk to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            NotFoundError: If the chunk is not found
            APIError: If the API request fails
        """
        self._delete(f"/api/chunks/{chunk_id}")
        return True
    
    # === Helper methods for HTTP requests ===
    
    def _get(self, endpoint: str, **kwargs) -> Any:
        """Make a GET request to the API"""
        return self._request("GET", endpoint, **kwargs)
    
    def _post(self, endpoint: str, **kwargs) -> Any:
        """Make a POST request to the API"""
        return self._request("POST", endpoint, **kwargs)
    
    def _patch(self, endpoint: str, **kwargs) -> Any:
        """Make a PATCH request to the API"""
        return self._request("PATCH", endpoint, **kwargs)
    
    def _delete(self, endpoint: str, **kwargs) -> Any:
        """Make a DELETE request to the API"""
        return self._request("DELETE", endpoint, **kwargs)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Make a request to the API with error handling.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Any: Response JSON data
            
        Raises:
            NotFoundError: If resource is not found (404)
            ValidationError: If validation fails (400)
            APIError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Return None for 204 No Content
            if response.status_code == 204:
                return None
                
            return response.json()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except ValueError:
                error_message = str(e)
            
            if status_code == 404:
                raise NotFoundError(error_message)
            elif status_code == 400:
                raise ValidationError(error_message)
            else:
                raise APIError(f"HTTP {status_code}: {error_message}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}") 