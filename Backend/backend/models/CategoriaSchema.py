from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoriaSchema(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class CategoriaPublic(CategoriaSchema):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class CategoriaUpdate(CategoriaSchema):
    update_at: datetime


class CategoriaList(BaseModel):
    categorias: list[CategoriaPublic]
