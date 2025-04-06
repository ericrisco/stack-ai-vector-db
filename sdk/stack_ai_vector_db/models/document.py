from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

class Document(BaseModel):
    """
    Represents a document which contains chunks of text
    """
    id: UUID = Field(default_factory=uuid4)
    library_id: UUID
    name: str
    chunks: List = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict) 