from datetime import date
from decimal import Decimal
from http import HTTPStatus
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database import get_session
from backend.middleware.security import validate_api_key
from backend.models.Filters import FilterPage
from backend.models.GastosSchema import (
    GastosListBot,
    GastosPublic,
    GastosPublicBot,
    GastosSchema,
    GastosUpdateSchema,
)
from backend.models.Mensages import Message
from backend.models.MetasSchemas import MetaList, MetaPublic, MetaSchema
from backend.models.UserSchema import UserPublic
from backend.models.models import Categorias, Gastos, Metas, User

router = APIRouter(prefix='/bot', tags=['bot'])

SessionType = Annotated[AsyncSession, Depends(get_session)]
APIKey = Annotated[bool, Depends(validate_api_key)]
FilterPageType = Annotated[FilterPage, Depends()]


@router.get('/by-id/{id}', response_model=UserPublic)
async def get_user_by_id(
    id: UUID,
    session: SessionType,
    api_key: APIKey,
):
    user = await session.scalar(select(User).where(User.id == id))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user


@router.post('/', response_model=GastosPublic, status_code=HTTPStatus.CREATED)
async def create_gasto(
    gastos: GastosSchema,
    session: SessionType,
    api_key: APIKey,
):
    """Cria gasto (rota para bot)"""

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

    gasto_obj = Gastos(**gastos.model_dump())
    session.add(gasto_obj)
    await session.commit()
    await session.refresh(gasto_obj)

    return gasto_obj

@router.get(
    '/gastos/{gasto_id}',
    response_model=GastosPublic,
    status_code=HTTPStatus.OK,
)
async def read_gasto_by_id( 
    gasto_id: UUID,
    session: SessionType,
    api_key: APIKey,
):
    """Busca um gasto específico pelo ID"""

    gasto = await session.get(Gastos, gasto_id)

    if not gasto:
        raise HTTPException(
            detail='Gasto not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    return gasto


@router.get(
    '/gastos/{gasto_id}',
    response_model=GastosPublic,
    status_code=HTTPStatus.OK,
)
async def read_gasto_by_id( 
    gasto_id: UUID,
    session: SessionType,
    api_key: APIKey,
):
    """Busca um gasto específico pelo ID - com eager loading da categoria"""
    
    # ← MUDANÇA AQUI: Use selectinload para carregar a categoria
    query = select(Gastos).options(selectinload(Gastos.categoria)).where(Gastos.id == gasto_id)
    result = await session.execute(query)
    gasto = result.scalar_one_or_none()
    
    if not gasto:
        raise HTTPException(
            detail='Gasto not found',
            status_code=HTTPStatus.NOT_FOUND,
        )
    
    # ← O schema GastosPublicBot ou similar deve incluir categoria_name
    return {
        'id': gasto.id,
        'message': gasto.message,
        'value': float(gasto.value),
        'categoria_id': gasto.categoria_id,
        'categoria_name': gasto.categoria.name,  # ← Agora isso funciona!
        'user_id': gasto.user_id,
        'created_at': gasto.created_at.isoformat(),
    }


@router.get(
    '/user/{user_id}',
    response_model=GastosListBot,
    status_code=HTTPStatus.OK,
)
async def read_gastos_by_user( # noqa: CÓDIGO_DO_ERRO
    user_id: UUID,
    session: SessionType,
    api_key: APIKey,
    filter_user: FilterPageType,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """Lista gastos por usuário com filtro de período (rota para bot)"""

    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            detail='User not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    query = (
        select(Gastos)
        .where(Gastos.user_id == user_id)
        .options(selectinload(Gastos.categoria))
        .order_by(Gastos.created_at.desc())
    )

    if start_date:
        query = query.where(func.date(Gastos.created_at) >= start_date)
    if end_date:
        query = query.where(func.date(Gastos.created_at) <= end_date)

    gastos = await session.scalars(
        query.limit(filter_user.limit).offset(filter_user.offset)
    )

    return {
        'gastos': [
            {
                'id': g.id,
                'message': g.message,
                'value': float(g.value),
                'categoria_id': g.categoria_id,
                'categoria_name': g.categoria.name,
                'user_id': g.user_id,
                'created_at': g.created_at.isoformat(),
            }
            for g in gastos.all()
        ]
    }


@router.get(
    '/user/{user_id}/ultimo-gasto',
    response_model=GastosListBot,
    status_code=HTTPStatus.OK,
)
async def read_ultimo_gasto_por_usuario(
    user_id: UUID,
    session: SessionType,
    api_key: APIKey,
):
    """Retorna o último gasto adicionado pelo usuário"""

    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            detail='User not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    gasto = await session.scalar(
        select(Gastos)
        .where(Gastos.user_id == user_id)
        .options(selectinload(Gastos.categoria))
        .order_by(Gastos.created_at.desc())
        .limit(1)
    )

    if not gasto:
        return {'gastos': []}

    return {
        'gastos': [
            {
                'id': gasto.id,
                'message': gasto.message,
                'value': float(gasto.value),
                'categoria_id': gasto.categoria_id,
                'categoria_name': gasto.categoria.name,
                'user_id': gasto.user_id,
                'created_at': gasto.created_at.isoformat(),
            }
        ]
    }


@router.put(
    '/gastos/{gasto_id}/{user_id}',
    response_model=GastosPublic,
    status_code=HTTPStatus.OK,
)
async def update_gasto_bot(
    session: SessionType,
    user_id: UUID,
    gasto_id: UUID,
    gasto: GastosUpdateSchema,
    api_key: APIKey,
):
    """Atualiza gasto (rota para bot)"""

    result = await session.scalars(select(Gastos).where(Gastos.id == gasto_id))
    db_gasto = result.first()

    if not db_gasto:
        raise HTTPException(
            detail='Gasto not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    if db_gasto.user_id != user_id:
        raise HTTPException(
            detail='Not permission',
            status_code=HTTPStatus.FORBIDDEN,
        )

    categoria = await session.scalar(
        select(Categorias).where(Categorias.id == gasto.categoria_id)
    )
    if not categoria:
        raise HTTPException(
            detail='Categoria not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    db_gasto.message = gasto.message
    db_gasto.value = gasto.value
    db_gasto.categoria_id = gasto.categoria_id

    session.add(db_gasto)
    await session.commit()
    await session.refresh(db_gasto)

    return db_gasto


@router.delete(
    '/gastos/{gasto_id}/{user_id}',
    response_model=Message,
    status_code=HTTPStatus.OK,
)
async def delete_gasto_bot(
    session: SessionType,
    user_id: UUID,
    gasto_id: UUID,
    api_key: APIKey,
):
    """Deleta gasto (rota para bot)"""

    result = await session.scalars(select(Gastos).where(Gastos.id == gasto_id))
    db_gasto = result.first()

    if not db_gasto:
        raise HTTPException(
            detail='Gasto not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    if db_gasto.user_id != user_id:
        raise HTTPException(
            detail='Not permission',
            status_code=HTTPStatus.FORBIDDEN,
        )

    await session.delete(db_gasto)
    await session.commit()

    return {'message': 'Gasto deleted'}


@router.post(
    '/metas',
    response_model=MetaPublic,
    status_code=HTTPStatus.CREATED,
)
async def create_meta_bot(
    meta: MetaSchema,
    session: SessionType,
    api_key: APIKey,
):
    """Cria meta (rota para bot)"""

    user = await session.scalar(select(User).where(User.id == meta.user_id))
    if not user:
        raise HTTPException(
            detail='User not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    meta_obj = Metas(**meta.model_dump())
    session.add(meta_obj)
    await session.commit()
    await session.refresh(meta_obj)

    return meta_obj


@router.get(
    '/metas/user/{user_id}',
    response_model=MetaList,
    status_code=HTTPStatus.OK,
)
async def read_metas_by_user_bot(
    session: SessionType,
    user_id: UUID,
    filter_user: FilterPageType,
    api_key: APIKey,
):
    """Lista metas por usuário (rota para bot)"""

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

    return {'metas': metas.all()}


@router.get(
    '/metas/{meta_id}',
    response_model=MetaPublic,
    status_code=HTTPStatus.OK,
)
async def read_meta_by_id(
    meta_id: UUID,
    session: SessionType,
    api_key: APIKey,
):
    """Busca uma meta específica pelo ID"""
    
    meta = await session.get(Metas, meta_id)

    if not meta:
        raise HTTPException(
            detail='Meta not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    return meta


@router.patch(
    '/metas/{meta_id}',
    response_model=MetaPublic,
    status_code=HTTPStatus.OK,
)
async def update_meta_bot(
    api_key: APIKey,
    session: SessionType,
    meta_id: UUID,
    value_actual: Annotated[Decimal, Query(ge=0)],
):
    """Atualiza valor atual da meta (rota para bot)"""

    result = await session.scalars(select(Metas).where(Metas.id == meta_id))
    db_meta = result.first()

    if not db_meta:
        raise HTTPException(
            detail='Meta not found',
            status_code=HTTPStatus.NOT_FOUND,
        )

    db_meta.value_actual = value_actual

    session.add(db_meta)
    await session.commit()
    await session.refresh(db_meta)

    return db_meta


@router.delete(
    '/metas/{meta_id}',
    response_model=Message,
    status_code=HTTPStatus.OK,
)
async def delete_meta_bot(
    session: SessionType,
    meta_id: UUID,
    api_key: APIKey,
):
    """Deleta meta (rota para bot)"""

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
