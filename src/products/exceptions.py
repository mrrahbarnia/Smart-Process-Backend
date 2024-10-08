from fastapi import HTTPException, status


class CommentNotCreated(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Comment didn't created successfully!"


class CommentNotOwner(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "Only owner of the comment able to delete it!"


class GuarantyNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no guaranty with the provided info!"
