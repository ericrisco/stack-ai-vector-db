from pydantic import BaseModel
from typing import List, Dict

class Chunk(BaseModel):
    id: int
    text: str
    embedding: List[float]
    metadata: Dict[str, str] 