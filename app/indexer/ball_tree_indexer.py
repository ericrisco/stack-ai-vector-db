import numpy as np
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from uuid import UUID

from app.indexer.indexer_interface import VectorIndexer
from app.models.chunk import Chunk
from app.models.library import Library
from app.services.library_service import LibraryService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService


class BallNode:
    """
    A node in the Ball Tree.
    
    Each node represents a ball (hypersphere) that contains points.
    """
    
    def __init__(
            self, 
            points: np.ndarray, 
            indices: List[int], 
            chunk_infos: List[Dict[str, Any]], 
            leaf_size: int = 40
        ):
        """
        Initialize a BallNode.
        
        Args:
            points: The embedding vectors contained in this node
            indices: The original indices of the vectors
            chunk_infos: The corresponding chunk information
            leaf_size: Max number of points in a leaf node
        """
        self.indices = indices
        self.chunk_infos = chunk_infos
        self.left = None
        self.right = None
        self.radius = 0.0
        self.center = None
        
        if len(indices) <= leaf_size:
            # This is a leaf node
            if len(indices) > 0:
                self.center = np.mean(points, axis=0)
                self.radius = np.max(np.linalg.norm(points - self.center, axis=1))
            else:
                # Empty node
                if points.shape[0] > 0:
                    self.center = np.zeros(points.shape[1], dtype=np.float32)
                else:
                    self.center = np.array([0], dtype=np.float32)
                self.radius = 0.0
            return
        
        # Choose a dimension with highest variance and split
        variances = np.var(points, axis=0)
        if np.all(variances == 0):
            # All points are the same, just make this a leaf node
            self.center = points[0].copy()
            self.radius = 0.0
            return
            
        split_dim = np.argmax(variances)
        
        # Sort points along the chosen dimension
        sorted_indices = np.argsort(points[:, split_dim])
        median_idx = len(sorted_indices) // 2
        
        # Ensure we don't create empty nodes
        if median_idx == 0:
            median_idx = 1
        elif median_idx == len(sorted_indices):
            median_idx = len(sorted_indices) - 1
        
        # Split points into left and right sets
        left_indices = [indices[i] for i in sorted_indices[:median_idx]]
        left_points = points[sorted_indices[:median_idx]]
        left_chunk_infos = [chunk_infos[i] for i in sorted_indices[:median_idx]]
        
        right_indices = [indices[i] for i in sorted_indices[median_idx:]]
        right_points = points[sorted_indices[median_idx:]]
        right_chunk_infos = [chunk_infos[i] for i in sorted_indices[median_idx:]]
        
        # Create child nodes
        self.left = BallNode(left_points, left_indices, left_chunk_infos, leaf_size)
        self.right = BallNode(right_points, right_indices, right_chunk_infos, leaf_size)
        
        # Calculate center and radius of this node
        self.center = np.mean(points, axis=0)
        self.radius = np.max(np.linalg.norm(points - self.center, axis=1))


class BallTree:
    """
    A Ball Tree implementation for efficient nearest neighbor searches.
    
    This is a spatial data structure that organizes points in a metric space by
    enclosing them in nested hyperspheres (balls).
    """
    
    def __init__(self, leaf_size: int = 40):
        """
        Initialize a Ball Tree.
        
        Args:
            leaf_size: Maximum number of points in a leaf node
        """
        self.root = None
        self.leaf_size = leaf_size
        self.points = None
        self.chunk_infos = None
        
    def build(self, 
             points: np.ndarray, 
             chunk_infos: List[Dict[str, Any]]) -> None:
        """
        Build the Ball Tree from a set of points.
        
        Args:
            points: The embedding vectors to index
            chunk_infos: The corresponding chunk information
        """
        if len(points) == 0:
            self.root = None
            return
            
        self.points = points
        self.chunk_infos = chunk_infos
        indices = list(range(len(points)))
        self.root = BallNode(points, indices, chunk_infos, self.leaf_size)
    
    def _search_node(self, 
                    node: BallNode, 
                    query: np.ndarray, 
                    k: int, 
                    results: List[Tuple[float, int]]) -> None:
        """
        Recursively search for k nearest neighbors in a node.
        
        Args:
            node: The current node to search
            query: The query vector
            k: Number of nearest neighbors to find
            results: List of (distance, index) tuples for the current best results
        """
        if node is None:
            return
            
        # Calculate distance to center of this ball
        dist_to_center = np.linalg.norm(query - node.center)
        
        # If this is a leaf node, check all points
        if node.left is None and node.right is None:
            for i in node.indices:
                # Check if index is valid
                if i >= len(self.points):
                    continue
                    
                center_i = self.points[i]
                dist = np.linalg.norm(query - center_i)
                
                if len(results) < k:
                    results.append((dist, i))
                    results.sort()
                elif dist < results[-1][0]:
                    results[-1] = (dist, i)
                    results.sort()
            return
        
        # Check if we have any results yet
        farthest_dist = float('inf')
        if results and len(results) >= k:
            farthest_dist = results[-1][0]
        
        # If we can't prune this node, search both children
        if len(results) < k or dist_to_center - node.radius <= farthest_dist:
            # Determine which child to search first (the closer one)
            left_dist = np.linalg.norm(query - node.left.center) if node.left else float('inf')
            right_dist = np.linalg.norm(query - node.right.center) if node.right else float('inf')
            
            # Update farthest_dist since it might have changed
            farthest_dist = float('inf')
            if results and len(results) >= k:
                farthest_dist = results[-1][0]
            
            if left_dist < right_dist:
                # Search closer child first
                if node.left:
                    self._search_node(node.left, query, k, results)
                
                # Update farthest dist after searching left
                farthest_dist = float('inf')
                if results and len(results) >= k:
                    farthest_dist = results[-1][0]
                    
                # Only search right if needed
                if node.right and (len(results) < k or right_dist - node.right.radius <= farthest_dist):
                    self._search_node(node.right, query, k, results)
            else:
                # Search closer child first
                if node.right:
                    self._search_node(node.right, query, k, results)
                
                # Update farthest dist after searching right
                farthest_dist = float('inf')
                if results and len(results) >= k:
                    farthest_dist = results[-1][0]
                    
                # Only search left if needed
                if node.left and (len(results) < k or left_dist - node.left.radius <= farthest_dist):
                    self._search_node(node.left, query, k, results)
    
    def search(self, 
              query: np.ndarray, 
              k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Search for k nearest neighbors to the query vector.
        
        Args:
            query: The query vector
            k: Number of nearest neighbors to find
            
        Returns:
            List of (distance, chunk_info) tuples for the k nearest neighbors
        """
        if self.root is None or self.points is None or self.chunk_infos is None:
            return []
            
        k = min(k, len(self.points))  # Ensure k is not larger than the number of points
        if k <= 0:
            return []
            
        results = []  # (distance, index) tuples
        self._search_node(self.root, query, k, results)
        
        # Convert results to (distance, chunk_info) tuples
        return [(dist, self.chunk_infos[idx]) for dist, idx in results if idx < len(self.chunk_infos)]


class BallTreeIndexer(VectorIndexer):
    """
    A vector indexer based on Ball Tree structure.
    
    Ball Trees organize points in nested hyperspheres, which can lead to efficient
    similarity searches in high-dimensional spaces by reducing the number of distance
    calculations needed.
    """
    
    def __init__(self, leaf_size: int = 40):
        self.trees = {}  # Map from library_id to Ball Tree
        self.vectors = {}  # Map from library_id to vector array
        self.chunk_info = {}  # Map from library_id to list of chunk info dicts
        self.leaf_size = leaf_size
        
    async def index_library(self, library_id: UUID) -> Dict[str, Any]:
        """
        Index all chunks in a library using a Ball Tree structure.
        
        Args:
            library_id: UUID of the library to index
            
        Returns:
            Dict containing indexing stats
        """
        start_time = time.time()
        
        # Get the library and verify it exists
        library = LibraryService.get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        
        # Get all documents in the library
        documents = DocumentService.get_documents_by_library(library_id)
        
        total_documents = len(documents)
        total_chunks = 0
        
        # Process all chunks to gather embeddings and metadata
        vectors = []
        self.chunk_info[library_id] = []
        
        for document in documents:
            for chunk in document.chunks:
                # Generate embedding if it doesn't exist
                embedding = chunk.embedding
                if not embedding:
                    embedding = await EmbeddingService.generate_embedding(chunk.text)
                
                vectors.append(embedding)
                
                # Store information about this chunk
                chunk_info = {
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "document_name": document.name,
                    "text": chunk.text,
                    "metadata": {
                        **chunk.metadata,
                        "document_metadata": document.metadata
                    }
                }
                self.chunk_info[library_id].append(chunk_info)
                total_chunks += 1
        
        # Build the Ball Tree
        if vectors:
            try:
                vectors_array = np.array(vectors, dtype=np.float32)
                self.vectors[library_id] = vectors_array
                tree = BallTree(leaf_size=self.leaf_size)
                tree.build(vectors_array, self.chunk_info[library_id])
                self.trees[library_id] = tree
                print(f"Built Ball Tree with {len(vectors)} vectors")
            except Exception as e:
                print(f"Error building Ball Tree: {str(e)}")
                self.trees[library_id] = None
        else:
            self.trees[library_id] = None
            self.vectors[library_id] = np.array([], dtype=np.float32)
            
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Return stats about this indexing operation
        stats = {
            "library_id": library_id,
            "library_name": library.name,
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "processing_time_seconds": processing_time,
            "indexer": self.get_indexer_name(),
            "leaf_size": self.leaf_size
        }
        
        return stats
    
    async def search(self, text: str, library_id: UUID, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for chunks similar to the provided text using the Ball Tree.
        
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
        
        results = []
        
        # If a specific library is provided, only search in that library
        if library_id not in self.trees or self.trees[library_id] is None:
            print(f"Library {library_id} not indexed or empty")
            return []
        
        # Verify we have vectors for the library
        if library_id not in self.vectors or len(self.vectors[library_id]) == 0:
            print(f"No vectors found for library {library_id}")
            return []
            
        # Search the Ball Tree
        try:
            print(f"Searching for {top_k} nearest neighbors")
            tree_results = self.trees[library_id].search(query_embedding, k=min(top_k, len(self.vectors[library_id])))
            print(f"Found {len(tree_results)} results")
        except Exception as e:
            print(f"Error searching Ball Tree: {str(e)}")
            return []
            
        # Safety check for empty results
        if not tree_results:
            return []
            
        # Convert to the expected output format
        for dist, chunk_info in tree_results:
            # Convert distance to similarity (higher is better)
            similarity = 1.0 / (1.0 + dist)  # Simple conversion that maps [0, inf) to (0, 1]
            
            results.append({
                "library_id": library_id,
                "similarity_score": float(similarity),
                "chunk_id": chunk_info["chunk_id"],
                "document_id": chunk_info["document_id"],
                "document_name": chunk_info["document_name"],
                "text": chunk_info["text"],
                "metadata": chunk_info["metadata"]
            })
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Add search metadata
        search_time = time.time() - start_time
        for result in results:
            result["search_metadata"] = {
                "search_time_seconds": search_time,
                "indexer": self.get_indexer_name()
            }
        
        return results
    
    def get_indexer_name(self) -> str:
        """
        Get the name of this indexer implementation.
        
        Returns:
            String name of the indexer
        """
        return "BALL_TREE"
    
    def get_indexer_info(self) -> Dict[str, Any]:
        """
        Get information about this indexer.
        
        Returns:
            Dictionary containing indexer information
        """
        indexed_libraries = len(self.trees)
        total_vectors = sum(
            len(self.chunk_info[lib_id]) 
            for lib_id in self.chunk_info if lib_id in self.trees and self.trees[lib_id] is not None
        )
        
        return {
            "name": self.get_indexer_name(),
            "description": "Ball Tree based vector search algorithm",
            "indexed_libraries": indexed_libraries,
            "total_vectors": total_vectors,
            "leaf_size": self.leaf_size,
            "algorithm_properties": {
                "exact_search": True,
                "complexity": "O(log n) average case",
                "distance_metric": "euclidean",
                "space_partitioning": "ball_tree"
            }
        } 