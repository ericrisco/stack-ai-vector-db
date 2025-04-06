from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from uuid import UUID, uuid4

class Chunk(BaseModel):
    """
    Represents a chunk of text with vector embedding
    """
    id: UUID = Field(default_factory=uuid4)
    document_id: Optional[UUID] = None
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict) 