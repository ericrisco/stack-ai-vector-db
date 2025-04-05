from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import UUID, uuid4
from app.models.document import Document

class Library(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    documents: List[Document] = []
    metadata: Dict[str, str] 