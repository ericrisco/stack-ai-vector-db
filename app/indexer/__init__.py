from typing import Dict, Type, Any

from app.indexer.indexer_interface import VectorIndexer
from app.indexer.brute_force_indexer import BruteForceIndexer
from app.indexer.ball_tree_indexer import BallTreeIndexer
from app.models.library import IndexerType

# Centralized registry of all available indexers
INDEXER_REGISTRY: Dict[IndexerType, Type[VectorIndexer]] = {
    IndexerType.BRUTE_FORCE: BruteForceIndexer,
    IndexerType.BALL_TREE: BallTreeIndexer,
}

# Default parameters for each indexer type
DEFAULT_INDEXER_PARAMS: Dict[IndexerType, Dict[str, Any]] = {
    IndexerType.BRUTE_FORCE: {},
    IndexerType.BALL_TREE: {"leaf_size": 40},
}

def create_indexer(indexer_type: IndexerType, **kwargs) -> VectorIndexer:
    """
    Create an indexer instance of the specified type with the given parameters.
    
    Args:
        indexer_type: The type of indexer to create
        **kwargs: Additional parameters to pass to the indexer constructor
    
    Returns:
        An instance of the specified indexer type
    
    Raises:
        ValueError: If the specified indexer type is not registered
    """
    if indexer_type not in INDEXER_REGISTRY:
        raise ValueError(f"Indexer type {indexer_type} not registered")
    
    # Get the indexer class
    indexer_class = INDEXER_REGISTRY[indexer_type]
    
    # Create and return an instance
    return indexer_class(**kwargs)

__all__ = [
    "VectorIndexer",
    "BruteForceIndexer",
    "BallTreeIndexer",
    "create_indexer",
    "INDEXER_REGISTRY"
] 