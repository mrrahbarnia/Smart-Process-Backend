from fastapi import HTTPException, status
from src.admin.config import admin_config


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


class BrandNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no brand with the provided info!"


class ImageSizeExc(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Image size limit is {admin_config.IMAGE_SIZE_LIMIT} KB!"


class MaximumImageNumberExc(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Maximum of uploaded images must be {admin_config.MAXIMUM_IMAGES}!"


class ImageFormatExc(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Image ext must be in {admin_config.IMAGE_FORMAT_LIMIT}!"


class ProductNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no product with the provided info!"


class DuplicateProductName(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique name for products!"


class DuplicateProductSerialNumber(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique serial number for products!"


class DuplicateGuarantySerial(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique guaranty serial!"


class TicketNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no ticket with the provided info!"


class DuplicateTagName(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique name for tags!"


class TagNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no tag with the provided info!"


class DuplicateArticleTagPk(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "PK unique for article_tags!"


class DuplicateArticleTitle(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Unique title for articles!"


class UniqueConstraintGlossaryTerms(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Term and article_id are unique together!"


class GlossaryNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no glossary with the provided info!"


class UniqueConstraintGlossary(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Term and article_id are unique together!"
