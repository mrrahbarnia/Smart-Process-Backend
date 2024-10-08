from typing import Annotated
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database import get_session
from src.tickets import schemas
from src.tickets import service

router = APIRouter()


@router.post(
    "/create-ticket/",
    status_code=status.HTTP_201_CREATED
)
async def create_ticket(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    payload: schemas.TicketIn
) -> dict:
    await service.create_ticket(
        session=session,
        payload=payload
    )
    return {"detail": "Created successfully."}
