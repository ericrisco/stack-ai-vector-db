from pydantic import BaseModel
from typing import List, Dict
from app.models.chunk import Chunk

class Document(BaseModel):
    id: int
    chunks: List[Chunk]
    metadata: Dict[str, str] 