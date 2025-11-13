from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.middleware.security import RoleChecker
from backend.models.CategoriaSchema import (
    CategoriaList,
    CategoriaPublic,
    CategoriaSchema,
)
from backend.models.Filters import FilterPage
from backend.models.Mensages import Message
from backend.models.models import Categorias, User
from backend.models.UserSchema import UserRole

router = APIRouter(prefix=('/categorias'), tags=['categorias'])

SessionType = Annotated[AsyncSession, Depends(get_session)]
AdminUserType = Annotated[User, Depends(RoleChecker([UserRole.ADMIN]))]
FilterPageType = Annotated[FilterPage, Query()]


@router.post(
    '/', response_model=CategoriaPublic, status_code=HTTPStatus.CREATED
)
async def create_categoria(
    categoria: CategoriaSchema,
    session: SessionType,
    current_user: AdminUserType,
):
    db_categoria = await session.scalar(
        select(Categorias).where(Categorias.name == categoria.name)
    )

    if db_categoria is not None:
        raise HTTPException(
            detail='Ja existe uma categoria registrada com esse nome',
            status_code=HTTPStatus.CONFLICT,
        )

    db_categoria = Categorias(**categoria.model_dump())

    session.add(db_categoria)
    await session.commit()
    await session.refresh(db_categoria)

    return db_categoria


@router.get('/', response_model=CategoriaList, status_code=HTTPStatus.OK)
async def read_categorias(
    session: SessionType,
    current_user: AdminUserType,
    filter_user: FilterPageType,
):
    categorias = await session.scalars(
        select(Categorias).limit(filter_user.limit).offset(filter_user.offset)
    )
    return {'categorias': categorias}


@router.get('/by-name/{name}')
async def get_categoria_by_name(name: str, session: SessionType):
    """Busca categoria por nome"""

    categoria = await session.scalar(
        select(Categorias).where(Categorias.name == name)
    )

    if not categoria:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Categoria '{name}' not found",
        )

    return {'id': str(categoria.id), 'nome': categoria.name}


@router.put(
    '/{categoria_id}',
    response_model=CategoriaPublic,
    status_code=HTTPStatus.OK,
)
async def update_user(
    session: SessionType,
    current_user: AdminUserType,
    categoria_id: UUID,
    categoria: CategoriaSchema,
):
    result = await session.scalars(
        select(Categorias).where(Categorias.id == categoria_id)
    )
    db_categoria = result.first()

    if not db_categoria:
        raise HTTPException(
            detail='A Categoria indicada nao existe',
            status_code=HTTPStatus.NOT_FOUND,
        )

    try:
        db_categoria.name = categoria.name

        session.add(db_categoria)
        await session.commit()
        await session.refresh(db_categoria)

        return db_categoria
    except IntegrityError:
        raise HTTPException(
            detail='Categoria already exist',
            status_code=HTTPStatus.CONFLICT,
        )


@router.delete(
    '/{categoria_id}', response_model=Message, status_code=HTTPStatus.OK
)
async def delete_user(
    session: SessionType,
    current_user: AdminUserType,
    categoria_id: UUID,
):
    result = await session.scalars(
        select(Categorias).where(Categorias.id == categoria_id)
    )
    db_categoria = result.first()

    if not db_categoria:
        raise HTTPException(
            detail='A Categoria indicada nao existe',
            status_code=HTTPStatus.NOT_FOUND,
        )

    await session.delete(db_categoria)
    await session.commit()

    return {'message': 'Categoria deleted'}
