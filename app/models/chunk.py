from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID, uuid4

class Chunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, str] 