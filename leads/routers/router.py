from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from leads.schemas.leads import (
    LeadCreate, LeadUpdate, LeadRead,
    LeadProductCreate, LeadProductUpdate, LeadProductRead,
    LeadStatusCreate, LeadStatusUpdate, LeadStatusRead
)
from leads.services.leads import LeadCRUD, LeadProductCRUD, LeadStatusCRUD
from user.models import User
from user.auth.fastapi_users_instance import fastapi_users

router = APIRouter(prefix="/leads", tags=["Leads"])


# Lead Endpoints
@router.get("/", response_model=list[LeadRead])
async def get_all_leads(
    session: AsyncSession = Depends(get_async_session)
):
    return await LeadCRUD.get_all(session)

@router.get("/{lead_id}", response_model=LeadRead)
async def get_one_lead(
    lead_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    lead = await LeadCRUD.get_by_id(session, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.post("/", response_model=LeadRead)
async def create_lead(
    data: LeadCreate, 
    session: AsyncSession = Depends(get_async_session),
):
    return await LeadCRUD.create(session, data)

@router.put("/{lead_id}", response_model=LeadRead)
async def update_lead(
    lead_id: int, 
    data: LeadUpdate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    updated = await LeadCRUD.update(session, lead_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated

@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: int, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    deleted = await LeadCRUD.delete(session, lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead not found")

# LeadProduct Endpoints
@router.get("/products/", response_model=list[LeadProductRead])
async def get_all_lead_products(
    session: AsyncSession = Depends(get_async_session)
):
    return await LeadProductCRUD.get_all(session)

@router.get("/products/{product_id}", response_model=LeadProductRead)
async def get_one_lead_product(
    product_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    product = await LeadProductCRUD.get_by_id(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Lead product not found")
    return product

@router.post("/products/", response_model=LeadProductRead)
async def create_lead_product(
    data: LeadProductCreate, 
    session: AsyncSession = Depends(get_async_session),
):
    return await LeadProductCRUD.create(session, data)

@router.put("/products/{product_id}", response_model=LeadProductRead)
async def update_lead_product(
    product_id: int, 
    data: LeadProductUpdate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    updated = await LeadProductCRUD.update(session, product_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead product not found")
    return updated

@router.delete("/products/{product_id}", status_code=204)
async def delete_lead_product(
    product_id: int, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    deleted = await LeadProductCRUD.delete(session, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead product not found")

# LeadStatus Endpoints
@router.get("/statuses/", response_model=list[LeadStatusRead])
async def get_all_lead_statuses(
    session: AsyncSession = Depends(get_async_session)
):
    return await LeadStatusCRUD.get_all(session)

@router.get("/statuses/{status_id}", response_model=LeadStatusRead)
async def get_one_lead_status(
    status_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    status = await LeadStatusCRUD.get_by_id(session, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Lead status not found")
    return status

@router.post("/statuses/", response_model=LeadStatusRead)
async def create_lead_status(
    data: LeadStatusCreate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await LeadStatusCRUD.create(session, data)

@router.put("/statuses/{status_id}", response_model=LeadStatusRead)
async def update_lead_status(
    status_id: int, 
    data: LeadStatusUpdate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    updated = await LeadStatusCRUD.update(session, status_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead status not found")
    return updated

@router.delete("/statuses/{status_id}", status_code=204)
async def delete_lead_status(
    status_id: int, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    deleted = await LeadStatusCRUD.delete(session, status_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead status not found")
    