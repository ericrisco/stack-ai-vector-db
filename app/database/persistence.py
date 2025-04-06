import json
import os
import logging
from pathlib import Path
from uuid import UUID

from app.database.db import get_db

# Configure logger
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = os.environ.get("DATA_DIR", "app/data")

def ensure_data_directory():
    """Ensure the data directory exists"""
    Path(DATA_DIR).mkdir(exist_ok=True)

def get_library_file_path(library_id: UUID) -> str:
    """Get the path to a library's JSON file"""
    return os.path.join(DATA_DIR, f"library_{library_id}.json")

def save_library(library_id: UUID) -> bool:
    """
    Save a library with its documents and chunks to a JSON file.
    
    Args:
        library_id: UUID of the library to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_data_directory()
        db = get_db()
        
        # Get library data
        with db.library_lock:
            library_data = db.libraries.get(library_id)
            if not library_data:
                logger.warning(f"Cannot save library {library_id}: not found")
                return False
            
            # Create serializable structure
            serializable_library = library_data.copy()
        
        # Find all documents for this library
        document_ids = []
        with db.document_lock:
            document_ids = [
                doc_id for doc_id, lib_id in db.document_library_map.items() 
                if lib_id == library_id and doc_id in db.documents
            ]
            
            # Get document data
            serializable_documents = []
            for doc_id in document_ids:
                doc_data = db.documents.get(doc_id)
                if doc_data:
                    doc_copy = doc_data.copy()
                    serializable_documents.append(doc_copy)
        
        # Get chunk data
        serializable_chunks = []
        with db.chunk_lock:
            for doc_id in document_ids:
                # Find all chunks for this document
                chunk_ids = [
                    chunk_id for chunk_id, doc_id_for_chunk in db.chunk_document_map.items() 
                    if doc_id_for_chunk == doc_id and chunk_id in db.chunks
                ]
                
                for chunk_id in chunk_ids:
                    chunk_data = db.chunks.get(chunk_id)
                    if chunk_data:
                        # Create copy without embedding
                        chunk_copy = chunk_data.copy()
                        if "embedding" in chunk_copy:
                            del chunk_copy["embedding"]
                        serializable_chunks.append(chunk_copy)
        
        # Assemble the complete data structure
        data_to_save = {
            "library": serializable_library,
            "documents": serializable_documents,
            "chunks": serializable_chunks
        }
        
        # Save to JSON file
        file_path = get_library_file_path(library_id)
        with open(file_path, 'w') as f:
            json.dump(data_to_save, f, default=str)
            
        logger.info(f"Successfully saved library {library_id} to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving library {library_id}: {str(e)}")
        return False

def load_library(library_id: UUID) -> bool:
    """
    Load a library with its documents and chunks from a JSON file.
    
    Args:
        library_id: UUID of the library to load
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        file_path = get_library_file_path(library_id)
        if not os.path.exists(file_path):
            logger.warning(f"Cannot load library {library_id}: file not found")
            return False
            
        # Load JSON file and create database entries
        return load_library_from_file(file_path)
        
    except Exception as e:
        logger.error(f"Error loading library {library_id}: {str(e)}")
        return False

def load_all_libraries() -> int:
    """
    Load all libraries from JSON files in the data directory.
    
    Returns:
        int: Number of libraries successfully loaded
    """
    try:
        ensure_data_directory()
        count = 0
        
        # Find all library files
        for file_name in os.listdir(DATA_DIR):
            if file_name.startswith("library_") and file_name.endswith(".json"):
                # Extract library ID from filename
                library_id_str = file_name[8:-5]  # Remove "library_" prefix and ".json" suffix
                try:
                    library_id = UUID(library_id_str)
                    if load_library(library_id):
                        count += 1
                except ValueError:
                    logger.warning(f"Invalid library ID in filename: {file_name}")
                    
        logger.info(f"Successfully loaded {count} libraries")
        return count
        
    except Exception as e:
        logger.error(f"Error loading libraries: {str(e)}")
        return 0

def load_library_from_file(file_path: str) -> bool:
    """
    Load a library with its documents and chunks from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing library data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return False
            
        # Load from JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        db = get_db()
        
        # 1. Load library first
        library_data = data.get("library")
        if not library_data or "id" not in library_data:
            logger.warning(f"Invalid library data in file: {file_path}")
            return False
        
        library_id = UUID(library_data["id"])
        with db.library_lock:
            db.libraries[library_id] = library_data
        
        # 2. Load documents
        for doc_data in data.get("documents", []):
            if "id" not in doc_data or "library_id" not in doc_data:
                logger.warning(f"Invalid document data in file: {file_path}")
                continue
                
            doc_id = UUID(doc_data["id"])
            lib_id = UUID(doc_data["library_id"])
            
            with db.document_lock:
                db.documents[doc_id] = doc_data
                db.document_library_map[doc_id] = lib_id
        
        # 3. Load chunks
        for chunk_data in data.get("chunks", []):
            if "id" not in chunk_data or "document_id" not in chunk_data:
                logger.warning(f"Invalid chunk data in file: {file_path}")
                continue
                
            chunk_id = UUID(chunk_data["id"])
            doc_id = UUID(chunk_data["document_id"])
            
            # Remove embedding field if it exists
            if "embedding" in chunk_data:
                del chunk_data["embedding"]
                
            with db.chunk_lock:
                db.chunks[chunk_id] = chunk_data
                db.chunk_document_map[chunk_id] = doc_id
        
        logger.info(f"Successfully loaded data from file: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error loading data from file {file_path}: {str(e)}")
        return False 