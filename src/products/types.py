from typing import NewType, TypedDict
from datetime import datetime
from uuid import UUID

# ==================== Models types ==================== #

ProductId = NewType("ProductId", UUID)
SerialNumber = NewType("SerialNumber", str)
BrandId = NewType("BrandId", int)
ProductImageId = NewType("ProductImageId", int)
CategoryId = NewType("CategoryId", int)
AttributeValueId = NewType("AttributeValueId", int)
CommentId = NewType("CommentId", int)

# ==================== Query result types ==================== #

class CommentListResponse(TypedDict):
    id: CommentId
    username: str
    message: str
    created_at: datetime
