from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.middleware.security import RoleChecker
from backend.models.Filters import FilterPage
from backend.models.Mensages import Message
from backend.models.MetasSchemas import (
    MetaList,
    MetaPublic,
    MetaSchema,
    MetaUpdateSchema,
)
from backend.models.models import Metas, User
from backend.models.UserSchema import UserRole

router = APIRouter(prefix=('/metas'), tags=['metas'])

SessionType = Annotated[AsyncSession, Depends(get_session)]
AdminUserType = Annotated[User, Depends(RoleChecker([UserRole.ADMIN]))]
FilterPageType = Annotated[FilterPage, Query()]


@router.post('/', response_model=MetaPublic, status_code=HTTPStatus.CREATED)
async def create_meta(
    meta: MetaSchema,
    session: SessionType,
    current_user: AdminUserType,
):
    user = await session.scalar(select(User).where(User.id == meta.user_id))

    if not user:
        raise HTTPException(
            detail='User not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    meta = Metas(**meta.model_dump())

    session.add(meta)
    await session.commit()
    await session.refresh(meta)

    return meta


@router.get('/', response_model=MetaList, status_code=HTTPStatus.OK)
async def read_metas(
    session: SessionType,
    current_user: AdminUserType,
    filter_user: FilterPageType,
):
    metas = await session.scalars(
        select(Metas).limit(filter_user.limit).offset(filter_user.offset)
    )

    return {'metas': metas}


@router.get('/{user_id}', response_model=MetaList, status_code=HTTPStatus.OK)
async def read_metas_by_user(
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

    metas = await session.scalars(
        select(Metas)
        .where(Metas.user_id == user_id)
        .limit(filter_user.limit)
        .offset(filter_user.offset)
    )

    return {'metas': metas}


@router.put(
    '/{meta_id}',
    response_model=MetaPublic,
    status_code=HTTPStatus.OK,
)
async def update_meta(
    session: SessionType,
    current_user: AdminUserType,
    meta_id: UUID,
    meta: MetaUpdateSchema,
):
    result = await session.scalars(select(Metas).where(Metas.id == meta_id))
    db_meta = result.first()

    if not db_meta:
        raise HTTPException(
            detail='Meta not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    db_meta.name = meta.name
    db_meta.value = meta.value
    db_meta.time = meta.time
    db_meta.value_actual = meta.value_actual

    session.add(db_meta)
    await session.commit()
    await session.refresh(db_meta)

    return db_meta


@router.delete('/{meta_id}', response_model=Message, status_code=HTTPStatus.OK)
async def delete_meta(
    session: SessionType,
    current_user: AdminUserType,
    meta_id: UUID,
):
    result = await session.scalars(select(Metas).where(Metas.id == meta_id))
    db_meta = result.first()

    if not db_meta:
        raise HTTPException(
            detail='Meta not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    await session.delete(db_meta)
    await session.commit()

    return {'message': 'Meta deleted'}
