from fastapi import APIRouter, Path, Body, HTTPException, Depends, Query
from typing import List, Optional, Dict
from uuid import UUID

from app.models.document import Document
from app.services.document_service import DocumentService
from app.routers.dependencies import verify_api_version

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("", response_model=Document, status_code=201, dependencies=[Depends(verify_api_version)])
async def create_document(document: Document = Body(...)):
    try:
        return DocumentService.create_document(document)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[Document], dependencies=[Depends(verify_api_version)])
async def get_all_documents():
    return DocumentService.get_all_documents()

@router.get("/library/{library_id}", response_model=List[Document], dependencies=[Depends(verify_api_version)])
async def get_documents_by_library(library_id: UUID = Path(..., description="The ID of the library to retrieve documents for")):
    return DocumentService.get_documents_by_library(library_id)

@router.get("/{document_id}", response_model=Document, dependencies=[Depends(verify_api_version)])
async def get_document(document_id: UUID = Path(..., description="The ID of the document to retrieve")):
    document = DocumentService.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
    return document

@router.patch("/{document_id}", response_model=Document, dependencies=[Depends(verify_api_version)])
async def update_document(
    document_id: UUID = Path(..., description="The ID of the document to update"),
    document_data: Dict = Body(..., description="Updated document data")
):
    try:
        document = DocumentService.update_document(document_id, document_data)
        if document is None:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        return document
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{document_id}", status_code=204, dependencies=[Depends(verify_api_version)])
async def delete_document(document_id: UUID = Path(..., description="The ID of the document to delete")):
    result = DocumentService.delete_document(document_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
    return None 