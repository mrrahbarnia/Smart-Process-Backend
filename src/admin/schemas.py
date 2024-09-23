from pydantic import BaseModel, ConfigDict, computed_field

from src.utils import slugify


class Brand(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "name": "Hikvision",
                "description": "This is the popular brand, Hikvision"
            }
        ]
    })
    name: str
    description: str

    @computed_field # type: ignore
    @property
    def slug(self) -> str:
        return slugify(self.name)
