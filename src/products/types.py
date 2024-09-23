from typing import NewType
from uuid import UUID

ProductId = NewType("ProductId", UUID)
SerialNumber = NewType("SerialNumber", str)
BrandId = NewType("BrandId", int)
ProductImageId = NewType("ProductImageId", int)
CategoryId = NewType("CategoryId", int)
AttributeId = NewType("AttributeId", int)
AttributeValueId = NewType("AttributeValueId", int)
CommentId = NewType("CommentId", int)