from fastapi import APIRouter, Path, Body, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any, Literal
from uuid import UUID
from fastapi.responses import JSONResponse

from app.models.library import Library, IndexStatus, IndexerType
from app.services.library_service import LibraryService
from app.routers.dependencies import verify_api_version

router = APIRouter(prefix="/libraries", tags=["Libraries"])

@router.post("", response_model=Library, status_code=201, dependencies=[Depends(verify_api_version)])
async def create_library(library: Library = Body(...)):
    try:
        return LibraryService.create_library(library)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[Library], dependencies=[Depends(verify_api_version)])
async def get_all_libraries():
    return LibraryService.get_all_libraries()

@router.get("/{library_id}", response_model=Library, dependencies=[Depends(verify_api_version)])
async def get_library(library_id: UUID = Path(..., description="The ID of the library to retrieve")):
    library = LibraryService.get_library(library_id)
    if library is None:
        raise HTTPException(status_code=404, detail=f"Library with ID {library_id} not found")
    return library

@router.patch("/{library_id}", response_model=Library, dependencies=[Depends(verify_api_version)])
async def update_library(
    library_id: UUID = Path(..., description="The ID of the library to update"),
    library_data: Dict = Body(..., description="Updated library data")
):
    try:
        library = LibraryService.update_library(library_id, library_data)
        if library is None:
            raise HTTPException(status_code=404, detail=f"Library with ID {library_id} not found")
        return library
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{library_id}", status_code=204, dependencies=[Depends(verify_api_version)])
async def delete_library(library_id: UUID = Path(..., description="The ID of the library to delete")):
    result = LibraryService.delete_library(library_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Library with ID {library_id} not found")
    return None

@router.post("/{library_id}/index", response_model=Dict[str, Any], dependencies=[Depends(verify_api_version)])
async def index_library(
    library_id: UUID,
    indexer_type: IndexerType = IndexerType.BRUTE_FORCE,
    leaf_size: int = Query(40, ge=10, le=1000, description="Leaf size for Ball Tree indexer")
):
    """
    Start indexing a library with specified indexer.
    """
    try:
        result = await LibraryService.start_indexing_library(
            library_id=library_id,
            indexer_type=indexer_type,
            leaf_size=leaf_size
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting indexing: {str(e)}")

@router.get("/{library_id}/index/status", response_model=Dict[str, Any], dependencies=[Depends(verify_api_version)])
async def get_indexing_status(library_id: UUID):
    """
    Get the current indexing status of a library.
    """
    try:
        return LibraryService.get_indexing_status(library_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving indexing status: {str(e)}")

@router.post("/{library_id}/search", response_model=List[Dict[str, Any]], dependencies=[Depends(verify_api_version)])
async def search_library(
    library_id: UUID,
    query_text: str = Query(..., min_length=1, description="Text to search for"),
    top_k: int = Query(5, ge=1, le=100, description="Number of results to return")
):
    """
    Search for similar content in an indexed library.
    """
    try:
        results = await LibraryService.search_library(
            library_id=library_id,
            query_text=query_text,
            top_k=top_k
        )
        return results
    except ValueError as e:
        if "not indexed" in str(e).lower() or "being indexed" in str(e).lower():
            # More specific status code for indexing-related issues
            raise HTTPException(status_code=409, detail=str(e))
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching library: {str(e)}") 