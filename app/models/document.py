from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import UUID, uuid4
from app.models.chunk import Chunk

class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    library_id: UUID
    chunks: List[Chunk] = []
    metadata: Dict[str, str] 