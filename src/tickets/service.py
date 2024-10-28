import logging
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from src.tickets import schemas
from src.tickets.models import Ticket
from src.tickets import exceptions

logger = logging.getLogger("tickets")


async def create_ticket(
        session: async_sessionmaker[AsyncSession],
        payload: schemas.TicketIn
) -> None:
    query = sa.insert(Ticket).values(
        {
            Ticket.name: payload.name,
            Ticket.product_serial: payload.product_serial if payload.product_serial else None,
            Ticket.phone_number: payload.phone_number if payload.phone_number else None,
            Ticket.guaranty_rating: payload.guaranty_rating,
            Ticket.repairs_rating: payload.repairs_rating,
            Ticket.notification_rating: payload.notification_rating,
            Ticket.personal_behavior_rating: payload.personal_behavior_rating,
            Ticket.services_rating: payload.services_rating,
            Ticket.smart_process_rating: payload.smart_process_rating,
            Ticket.criticism: payload.criticism,
            Ticket.call_request: payload.call_request
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
    except IntegrityError as ex:
        logger.warning(ex)
        raise exceptions.TicketCreateException
