from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import HTTPException
from typing import List
from docs.models import Document
from docs.schemas.documents import DocumentCreate, DocumentUpdate, DocumentResponse


class DocumentCrud:
    async def create_document(document: DocumentCreate, db: AsyncSession) -> Document:
        db_document = Document(
            slug=document.slug,
            title=document.title,
            content=document.content,
            is_active=document.is_active
        )
        db.add(db_document)
        await db.commit()
        await db.refresh(db_document)
        return db_document

    async def get_document_by_id(document_id: int, db: AsyncSession) -> Document:
        result = await db.execute(select(Document).filter(Document.id == document_id))
        document = result.scalars().first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    async def get_document_by_slug(slug: str, db: AsyncSession) -> Document:
        result = await db.execute(select(Document).filter(Document.slug == slug))
        document = result.scalars().first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    async def get_all_documents(db: AsyncSession) -> List[Document]:
        result = await db.execute(select(Document))
        return result.scalars().all()

    async def update_document(document_id: int, document_update: DocumentUpdate, db: AsyncSession) -> Document:
        result = await db.execute(select(Document).filter(Document.id == document_id))
        db_document = result.scalars().first()
        if not db_document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        update_data = document_update.dict(exclude_unset=True)
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(db_document)
        return db_document

    async def delete_document(document_id: int, db: AsyncSession) -> None:
        result = await db.execute(select(Document).filter(Document.id == document_id))
        document = result.scalars().first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        await db.execute(delete(Document).where(Document.id == document_id))
        await db.commit()