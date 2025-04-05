import threading
from typing import Dict
from uuid import UUID

class DB:
    def __init__(self):
        self.libraries: Dict[UUID, Dict] = {}
        self.documents: Dict[UUID, Dict] = {}
        self.chunks: Dict[UUID, Dict] = {}
        self.library_lock = threading.Lock()
        self.document_lock = threading.Lock()
        self.chunk_lock = threading.Lock()
        
        # Track relationships
        self.document_library_map: Dict[UUID, UUID] = {}  # document_id -> library_id
        self.chunk_document_map: Dict[UUID, UUID] = {}    # chunk_id -> document_id

# Create a singleton instance of the database
_db_instance = DB()

def get_db() -> DB:
    return _db_instance 