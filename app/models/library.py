from pydantic import BaseModel
from typing import List, Dict
from app.models.document import Document

class Library(BaseModel):
    id: int
    name: str
    documents: List[Document]
    metadata: Dict[str, str] 