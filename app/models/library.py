from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum
from app.models.document import Document

class IndexerType(str, Enum):
    """
    Enumeration of available vector indexer types
    """
    BRUTE_FORCE = "BRUTE_FORCE"
    BALL_TREE = "BALL_TREE"

class IndexStatus(BaseModel):
    """
    Represents the indexing status of a library
    """
    indexed: bool = False
    indexer_type: Optional[IndexerType] = None
    last_indexed: Optional[float] = None
    indexing_in_progress: bool = False

class Library(BaseModel):
    """
    Represents a library which contains multiple documents
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    documents: List[Document] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    index_status: IndexStatus = Field(default_factory=IndexStatus) 