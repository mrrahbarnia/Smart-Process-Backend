from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )
