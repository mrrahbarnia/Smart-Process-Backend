from fastapi import HTTPException, status


class UniqueConstraintBrandName(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique name for brands!"


class DuplicateCategoryName(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique name for categories!"


class InvalidParentCategoryName(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Invalid parent category name!"


class CategoryNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no category with the provided ID!"


class CannotDeleteParentCategory(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "Check Check Check"


class DuplicateAttributeName(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique name for attributes!"


class AttributeNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no attribute with the provided info!"


class CategoryAttributeUniqueTogether(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "category_id and attribute_id are unique together!"


class UnassignedWentWrong(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Unassign category and attribute went wrong!"