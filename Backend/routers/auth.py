from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.database import get_session
from Backend.middleware.security import (
    create_access_token,
    get_current_user,
    verify_password,
)
from Backend.models.models import User
from Backend.models.TokenSchema import Token

router = APIRouter(prefix=('/auth'), tags=['auth'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Current_User = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2Form,
    session: T_Session,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(
        data={'sub': user.email}, role=user.role
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: T_Current_User):
    new_access_token = create_access_token(
        data={'sub': user.email}, role=user.role
    )

    return {'access_token': new_access_token, 'token_type': 'bearer'}
