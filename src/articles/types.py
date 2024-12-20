from typing import NewType
from uuid import UUID

ArticleId = NewType("ArticleId", UUID)
ArticleImageId = NewType("ArticleImageId", int)
RatingId = NewType("RatingId", int)
ArticleCommentId = NewType("ArticleCommentId", int)
GlossaryId = NewType("GlossaryId", int)

