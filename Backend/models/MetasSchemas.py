from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MetaSchema(BaseModel):
    """Schema para retornar meta (INPUT)"""

    name: str = Field()
    value: Decimal = Field(gt=0)
    value_actual: Decimal = Field(ge=0)
    time: date
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class MetaPublic(MetaSchema):
    """Schema para retornar meta (OUTPUT)"""

    id: UUID

    model_config = ConfigDict(from_attributes=True)


class MetaUpdateSchema(BaseModel):
    """Schema para atualizar meta (INPUT)"""

    name: str = Field()
    value: Decimal = Field(gt=0)
    value_actual: Decimal = Field(ge=0)
    time: date


class MetaList(BaseModel):
    """Schema para retornar metas em lista (OUTPUT)"""

    metas: list[MetaPublic]
