from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.settings import Settings
from backend.models.models import User
from backend.models.UserSchema import UserRole

settings = Settings()

pwd_context = PasswordHash.recommended()

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl='/auth/token', refreshUrl='auth/refresh'
)

T_Session = Annotated[AsyncSession, Depends(get_session)]


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# Adicionar role no token
def create_access_token(data: dict, role: UserRole):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire, 'role': role})
    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    session: T_Session,
    token: str = Depends(oauth2_schema),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_email: str = payload.get('sub')
        token_role: str = payload.get('role')
        if not subject_email:
            raise credentials_exception
    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if token_role != user.role.value:
        raise credentials_exception

    if not user:
        raise credentials_exception

    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Insufficient permissions',
            )
        return user


async def validate_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='API Key header is missing',
        )

    if api_key != settings.BOT_API_KEY:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid API Key'
        )

    return True
