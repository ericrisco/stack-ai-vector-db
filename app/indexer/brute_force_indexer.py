import numpy as np
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from app.indexer.indexer_interface import VectorIndexer
from app.models.chunk import Chunk
from app.models.library import Library, IndexerType
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService

class BruteForceIndexer(VectorIndexer):
    """
    A brute force vector indexer that compares query vectors with all indexed vectors.
    This is a simple but inefficient implementation, best used for small libraries or as a baseline.
    """
    
    def __init__(self):
        self.vectors = {}  
        self.chunk_info = {}
        
    async def index_library(self, library_id: UUID) -> Dict[str, Any]:
        """
        Index all chunks in a library by retrieving their vectors.
        
        Args:
            library_id: UUID of the library to index
            
        Returns:
            Dict containing indexing stats
        """
        start_time = time.time()
        
        from app.services.library_service import LibraryService
        
        # Get the library and verify it exists
        library = LibraryService.get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        
        # Get all documents in the library
        documents = DocumentService.get_documents_by_library(library_id)
        
        total_documents = len(documents)
        total_chunks = 0
        total_embeddings_generated = 0
        
        # Initialize storage for this library
        self.vectors[library_id] = []
        self.chunk_info[library_id] = []
        
        # Process each document and its chunks
        for document in documents:
            for chunk in document.chunks:
                # Generate embedding if it doesn't exist
                embedding = chunk.embedding
                if not embedding:
                    embedding = await EmbeddingService.generate_embedding(chunk.text)
                    total_embeddings_generated += 1
                
                # Add chunk vector and metadata to our index
                self.vectors[library_id].append(np.array(embedding, dtype=np.float32))
                
                # Store information about this chunk for retrieval during search
                self.chunk_info[library_id].append({
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "document_name": document.name,
                    "text": chunk.text,
                    "metadata": {
                        **chunk.metadata,
                        "document_metadata": document.metadata
                    }
                })
                
                total_chunks += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Store stats about this indexing operation
        stats = {
            "library_id": library_id,
            "library_name": library.name,
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "total_embeddings_generated": total_embeddings_generated,
            "processing_time_seconds": processing_time,
            "indexer": self.get_indexer_name()
        }
        
        return stats
    
    async def search(self, text: str, library_id: UUID, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for chunks similar to the provided text using cosine similarity.
        
        Args:
            text: Text to search for (will be converted to embedding)
            library_id: Library ID to limit the search scope
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing search results
        """
        start_time = time.time()
        
        # Convert the search text to a vector embedding
        query_vector = await EmbeddingService.generate_embedding(text, input_type="search_query")
        query_embedding = np.array(query_vector, dtype=np.float32)
        
        # Normalize the query vector for cosine similarity
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
        
        results = []
        
        # If a specific library is provided, only search in that library
        library_ids = [library_id] if library_id else list(self.vectors.keys())
        
        for lib_id in library_ids:
            if lib_id not in self.vectors or not self.vectors[lib_id]:
                continue
                
            # Stack all vectors for efficient computation
            lib_vectors = np.vstack(self.vectors[lib_id])
            
            # Normalize all vectors for cosine similarity
            vector_norms = np.linalg.norm(lib_vectors, axis=1, keepdims=True)
            vector_norms[vector_norms == 0] = 1.0  # Avoid division by zero
            normalized_vectors = lib_vectors / vector_norms
            
            # Compute cosine similarities (dot product of normalized vectors)
            similarities = np.dot(normalized_vectors, query_embedding)
            
            # Find the indices of the top_k highest similarities
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Add results to the list
            for idx in top_indices:
                chunk_metadata = self.chunk_info[lib_id][idx]
                results.append({
                    "library_id": lib_id,
                    "similarity_score": float(similarities[idx]),
                    "chunk_id": chunk_metadata["chunk_id"],
                    "document_id": chunk_metadata["document_id"],
                    "document_name": chunk_metadata["document_name"],
                    "text": chunk_metadata["text"],
                    "metadata": chunk_metadata["metadata"]
                })
        
        # Sort all results by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Limit to top_k results overall
        results = results[:top_k]
        
        # Add search metadata
        search_time = time.time() - start_time
        for result in results:
            result["search_metadata"] = {
                "search_time_seconds": search_time,
                "indexer": self.get_indexer_name()
            }
        
        return results
        
    def get_indexer_name(self) -> IndexerType:
        """
        Get the name of this indexer implementation.
        
        Returns:
            IndexerType enum value for this indexer
        """
        return IndexerType.BRUTE_FORCE
        
    def get_indexer_info(self) -> Dict[str, Any]:
        """
        Get information about this indexer.
        
        Returns:
            Dictionary containing indexer information
        """
        indexed_libraries = len(self.vectors)
        total_vectors = sum(len(vectors) for vectors in self.vectors.values())
        
        return {
            "name": self.get_indexer_name(),
            "description": "Simple brute force vector search algorithm",
            "indexed_libraries": indexed_libraries,
            "total_vectors": total_vectors,
            "algorithm_properties": {
                "exact_search": True,
                "complexity": "O(n*d)",
                "distance_metric": "cosine_similarity"
            }
        }