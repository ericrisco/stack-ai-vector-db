from fastapi import APIRouter, Path, Body, HTTPException, Depends, Query
from typing import List, Optional, Dict
from uuid import UUID

from app.models.chunk import Chunk
from app.services.chunk_service import ChunkService
from app.routers.dependencies import verify_api_version

router = APIRouter(prefix="/chunks", tags=["Chunks"])

@router.post("", response_model=Chunk, status_code=201, dependencies=[Depends(verify_api_version)])
async def create_chunk(chunk: Chunk = Body(...)):
    try:
        return ChunkService.create_chunk(chunk)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch", response_model=List[Chunk], status_code=201, dependencies=[Depends(verify_api_version)])
async def create_chunks(chunks: List[Chunk] = Body(...)):
    try:
        return ChunkService.create_chunks(chunks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[Chunk], dependencies=[Depends(verify_api_version)])
async def get_all_chunks():
    return ChunkService.get_all_chunks()

@router.get("/document/{document_id}", response_model=List[Chunk], dependencies=[Depends(verify_api_version)])
async def get_chunks_by_document(document_id: UUID = Path(..., description="The ID of the document to retrieve chunks for")):
    return ChunkService.get_chunks_by_document(document_id)

@router.get("/{chunk_id}", response_model=Chunk, dependencies=[Depends(verify_api_version)])
async def get_chunk(chunk_id: UUID = Path(..., description="The ID of the chunk to retrieve")):
    chunk = ChunkService.get_chunk(chunk_id)
    if chunk is None:
        raise HTTPException(status_code=404, detail=f"Chunk with ID {chunk_id} not found")
    return chunk

@router.patch("/{chunk_id}", response_model=Chunk, dependencies=[Depends(verify_api_version)])
async def update_chunk(
    chunk_id: UUID = Path(..., description="The ID of the chunk to update"),
    chunk_data: Dict = Body(..., description="Updated chunk data")
):
    try:
        chunk = ChunkService.update_chunk(chunk_id, chunk_data)
        if chunk is None:
            raise HTTPException(status_code=404, detail=f"Chunk with ID {chunk_id} not found")
        return chunk
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{chunk_id}", status_code=204, dependencies=[Depends(verify_api_version)])
async def delete_chunk(chunk_id: UUID = Path(..., description="The ID of the chunk to delete")):
    result = ChunkService.delete_chunk(chunk_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Chunk with ID {chunk_id} not found")
    return None 