# backend/models/GastosSchema.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GastosSchema(BaseModel):
    """Schema para criar gasto (INPUT)"""

    message: str = Field(min_length=1, max_length=400)
    value: Decimal = Field(gt=0)
    categoria_id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class GastosUpdateSchema(BaseModel):
    """Schema para atualizar gasto"""

    message: str = Field(min_length=1, max_length=400)
    value: Decimal = Field(gt=0)
    categoria_id: UUID

    model_config = ConfigDict(from_attributes=True)


class GastosPublic(BaseModel):
    """Schema para retornar gasto (OUTPUT)"""

    id: UUID
    message: str
    value: Decimal
    categoria_id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GastosPublicBot(BaseModel):
    """Schema para retornar gasto (OUTPUT)"""

    id: UUID
    message: str
    value: Decimal
    categoria_id: UUID
    categoria_name: str
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GastosList(BaseModel):
    gastos: list[GastosPublic]

    model_config = ConfigDict(from_attributes=True)


class GastosListBot(BaseModel):
    gastos: list[GastosPublicBot]
