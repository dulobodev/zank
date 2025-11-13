from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.middleware.security import RoleChecker
from backend.models.Filters import FilterPage
from backend.models.GastosSchema import (
    GastosList,
    GastosPublic,
    GastosSchema,
    GastosUpdateSchema,
)
from backend.models.Mensages import Message
from backend.models.models import Categorias, Gastos, User
from backend.models.UserSchema import UserRole

router = APIRouter(prefix=('/gastos'), tags=['gastos'])

SessionType = Annotated[AsyncSession, Depends(get_session)]
AdminUserType = Annotated[User, Depends(RoleChecker([UserRole.ADMIN]))]
FilterPageType = Annotated[FilterPage, Query()]


@router.post('/', response_model=GastosPublic, status_code=HTTPStatus.CREATED)
async def create_gasto(
    gastos: GastosSchema,
    session: SessionType,
    current_user: AdminUserType,
):
    user = await session.scalar(select(User).where(User.id == gastos.user_id))

    if not user:
        raise HTTPException(
            detail='User not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    categoria = await session.scalar(
        select(Categorias).where(Categorias.id == gastos.categoria_id)
    )

    if not categoria:
        raise HTTPException(
            detail='Categoria not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    gastos = Gastos(**gastos.model_dump())

    session.add(gastos)
    await session.commit()
    await session.refresh(gastos)

    return gastos


@router.get('/', response_model=GastosList, status_code=HTTPStatus.OK)
async def read_gasto(
    session: SessionType,
    current_user: AdminUserType,
    filter_user: FilterPageType,
):
    result = await session.scalars(
        select(Gastos).limit(filter_user.limit).offset(filter_user.offset)
    )

    return {'gastos': result}


@router.get('/{user_id}', response_model=GastosList, status_code=HTTPStatus.OK)
async def read_gasto_by_user(
    session: SessionType,
    current_user: AdminUserType,
    user_id: UUID,
    filter_user: FilterPageType,
):
    user = await session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            detail='User not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    gastos = await session.scalars(
        select(Gastos)
        .where(Gastos.user_id == user_id)
        .limit(filter_user.limit)
        .offset(filter_user.offset)
    )
    return {'gastos': gastos}


@router.put(
    '/{gastos_id}',
    response_model=GastosPublic,
    status_code=HTTPStatus.OK,
)
async def update_gasto(
    session: SessionType,
    current_user: AdminUserType,
    gastos_id: UUID,
    gasto: GastosUpdateSchema,
):
    result = await session.scalars(
        select(Gastos).where(Gastos.id == gastos_id)
    )
    db_gastos = result.first()

    if not db_gastos:
        raise HTTPException(
            detail='Gasto not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    categoria = await session.scalars(
        select(Gastos).where(Gastos.categoria_id == gasto.categoria_id)
    )
    db_categoria = categoria.first()

    if not db_categoria:
        raise HTTPException(
            detail='Categoria not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    db_gastos.message = gasto.message
    db_gastos.value = gasto.value
    db_gastos.categoria_id = gasto.categoria_id

    session.add(db_gastos)
    await session.commit()
    await session.refresh(db_gastos)

    return db_gastos


@router.delete(
    '/{gastos_id}', response_model=Message, status_code=HTTPStatus.OK
)
async def delete_gasto(
    session: SessionType,
    current_user: AdminUserType,
    gastos_id: UUID,
):
    result = await session.scalars(
        select(Gastos).where(Gastos.id == gastos_id)
    )
    db_gastos = result.first()

    if not db_gastos:
        raise HTTPException(
            detail='Gasto not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    await session.delete(db_gastos)
    await session.commit()

    return {'message': 'Gastos deleted'}
