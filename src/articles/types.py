from typing import NewType
from uuid import UUID

ArticleId = NewType("ArticleId", UUID)
ArticleImageId = NewType("ArticleImageId", int)
TagId = NewType("TagId", int)
RatingId = NewType("RatingId", int)
ArticleCommentId = NewType("ArticleCommentId", int)
# GlossaryId = NewType("GlossaryId", int)