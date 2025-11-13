from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.middleware.security import (
    RoleChecker,
    get_current_user,
    get_password_hash,
)
from backend.models.Filters import FilterPage
from backend.models.Mensages import Message
from backend.models.models import User
from backend.models.UserSchema import (
    UserList,
    UserPublic,
    UserRole,
    UserSchema,
    UserSubscription,
)

router = APIRouter(prefix=('/users'), tags=['users'])

SessionType = Annotated[AsyncSession, Depends(get_session)]
Current_UserType = Annotated[User, Depends(get_current_user)]
FilterPageType = Annotated[FilterPage, Query()]
AdminUserType = Annotated[User, Depends(RoleChecker([UserRole.ADMIN]))]


@router.post('/', response_model=UserPublic, status_code=HTTPStatus.CREATED)
async def create_user(user: UserSchema, session: SessionType):
    db_user_email = await session.scalar(
        select(User).where((User.email == user.email))
    )

    db_user_phone = await session.scalar(
        select(User).where((User.phone == user.phone))
    )

    if db_user_email is not None:
        raise HTTPException(
            detail='Ja existe uma conta registrada com esse email',
            status_code=HTTPStatus.CONFLICT,
        )

    if db_user_phone is not None:
        raise HTTPException(
            detail='Este telefone já está cadastrado',
            status_code=HTTPStatus.CONFLICT,
        )

    db_user = User(**user.model_dump())
    db_user.password = get_password_hash(db_user.password)
    db_user.role = UserRole.ADMIN
    db_user.subscription_active = False
    db_user.subscription_expires_at = None

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList, status_code=HTTPStatus.OK)
async def read_users(
    session: SessionType,
    current_user: AdminUserType,
    filter_user: FilterPageType,
):
    users = await session.scalars(
        select(User).limit(filter_user.limit).offset(filter_user.offset)
    )
    return {'users': users}


@router.get('/by-phone/{phone}', response_model=UserSubscription)
async def get_user_by_phone(
    phone: str,
    session: SessionType,
):
    user = await session.scalar(select(User).where(User.phone == phone))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user


@router.put('/{user_id}', response_model=UserPublic, status_code=HTTPStatus.OK)
async def update_user(
    session: SessionType,
    current_user: Current_UserType,
    user_id: UUID,
    user: UserSchema,
):
    if current_user.id != user_id:
        raise HTTPException(
            detail='Not enough permissions', status_code=HTTPStatus.FORBIDDEN
        )
    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            detail='Email already exist',
            status_code=HTTPStatus.CONFLICT,
        )


@router.delete('/{user_id}', response_model=Message, status_code=HTTPStatus.OK)
async def delete_user(
    session: SessionType,
    current_user: Current_UserType,
    user_id: UUID,
):
    if current_user.id != user_id:
        raise HTTPException(
            detail='Not enough permissions', status_code=HTTPStatus.FORBIDDEN
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}
