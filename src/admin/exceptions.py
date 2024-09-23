from fastapi import HTTPException, status


class UniqueConstraintBrandName(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique name for brands!"
