from fastapi import APIRouter, Path, Body, HTTPException, Depends
from typing import List, Optional, Dict
from uuid import UUID

from app.models.library import Library
from app.services.library_service import LibraryService
from app.routers.dependencies import verify_api_version

router = APIRouter(prefix="/libraries", tags=["Libraries"])

@router.post("", response_model=Library, status_code=201, dependencies=[Depends(verify_api_version)])
async def create_library(library: Library = Body(...)):
    try:
        return LibraryService.create_library(library)
    except ValueError as e:
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