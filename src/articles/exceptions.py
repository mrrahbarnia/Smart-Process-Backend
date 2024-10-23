from fastapi import HTTPException, status


class ArticleNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no article with the provided ID!"