from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import UUID, uuid4

class Chunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    text: str
    embedding: List[float]
    metadata: Dict[str, str] 