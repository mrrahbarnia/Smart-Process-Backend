from fastapi import HTTPException, status


class TicketCreateException(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Something went wrong!"