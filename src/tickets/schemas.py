from typing import Annotated, Self
from pydantic import field_validator, model_validator, Field

from src.schemas import CustomBaseModel
from src.tickets.types import TicketId
from src.products.types import SerialNumber
from src.auth.types import PhoneNumber


class TicketIn(CustomBaseModel):
    name: Annotated[str, Field(max_length=200)]
    product_serial: Annotated[SerialNumber | None, Field(max_length=150, alias="productSerial")] = None
    phone_number: Annotated[PhoneNumber | None, Field(alias="phoneNumber")] = None
    guaranty_rating: Annotated[int, Field(alias="guarantyRating", le=5, ge=1)]
    repairs_rating: Annotated[int, Field(alias="repairsRating", le=5, ge=1)]
    notification_rating: Annotated[int, Field(alias="notificationRating", le=5, ge=1)]
    personal_behavior_rating: Annotated[int, Field(alias="personalBehaviorRating", le=5, ge=1)]
    services_rating: Annotated[int, Field(alias="servicesRating", le=5, ge=1)]
    smart_process_rating: Annotated[int, Field(alias="smartProcessRating", le=5, ge=1)]
    criticism: str
    call_request: Annotated[bool, Field(alias="callRequest")]

    @field_validator("phone_number", mode="after")
    @classmethod
    def validate_phone_length(cls, phone_number: PhoneNumber) -> PhoneNumber:
        if phone_number and len(phone_number) != 11:
            raise ValueError("Phone number must has exact 11 length!")
        return phone_number

    @model_validator(mode="after")
    def validate_call_request_with_entered_phone_number(self) -> Self:
        phone_number = self.phone_number
        call_request = self.call_request
        if not phone_number and call_request:
            raise ValueError("Could't request call without entering phone_number!")
        return self


class TicketList(TicketIn):
    id: TicketId
