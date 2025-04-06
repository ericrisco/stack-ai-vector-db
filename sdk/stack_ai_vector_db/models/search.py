from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from uuid import UUID

class DocumentInfo(BaseModel):
    """
    Simplified document information for search results.
    Contains only the essential metadata about a document.
    """
    id: str = Field(..., description="ID of the document")
    name: str = Field(..., description="Name of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")

class SearchResult(BaseModel):
    """
    Model for search results with simplified output format.
    Contains only the essential information about the matching chunk.
    """
    chunk_id: str = Field(..., description="ID of the matching chunk")
    text: str = Field(..., description="Text content of the chunk")
    score: float = Field(..., description="Similarity score between query and chunk")
    document: DocumentInfo = Field(..., description="Document information") 