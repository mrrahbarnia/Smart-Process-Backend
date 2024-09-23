from pydantic import BaseModel, computed_field

from src.utils import slugify


# class BrandList(BaseModel):
#     name: str
#     description:

#     @computed_field # type: ignore
#     @property
#     def slug(self) -> str:
#         return slugify(self.name)