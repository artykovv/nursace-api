from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, APIRouter
from typing import List
from config.database import get_async_session
from docs.schemas.documents import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse
from docs.services.documetns import DocumentCrud

from user.auth.fastapi_users_instance import fastapi_users
from user.auth.auth import auth_backend
from user.models import User

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=DocumentResponse)
async def create_document_endpoint(
    document: DocumentCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    try:
        return await DocumentCrud.create_document(document, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_endpoint(
    document_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    return await DocumentCrud.get_document_by_id(document_id, db)

@router.get("/slug/{slug}", response_model=DocumentResponse)
async def get_document_by_slug_endpoint(
    slug: str,
    db: AsyncSession = Depends(get_async_session)
):
    return await DocumentCrud.get_document_by_slug(slug, db)

@router.get("/", response_model=List[DocumentListResponse])
async def get_all_documents_endpoint(
    db: AsyncSession = Depends(get_async_session)
):
    return await DocumentCrud.get_all_documents(db)

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document_endpoint(
    document_id: int,
    document: DocumentUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await DocumentCrud.update_document(document_id, document, db)

@router.delete("/{document_id}")
async def delete_document_endpoint(
    document_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    await DocumentCrud.delete_document(document_id, db)
    return {"message": "Document deleted successfully"}