import re
from enum import Enum
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

PHONE_DIGITS = 11  # Celular com DDD (ex: 11987654321)
MIN_DDD = 11
MAX_DDD = 99


def validate_strong_password(password: str) -> str:
    """Valida força da senha."""
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[#?!@$%^&*-]).{8,}$'

    if not re.match(pattern, password):
        raise ValueError(
            'Senha inválida: precisa de 8+ caracteres, '
            'maiúscula, minúscula, número e caractere especial'
        )

    return password


def validate_phone(v: str) -> str:
    # Remove caracteres não numéricos
    phone_numbers = re.sub(r'\D', '', v)

    if len(phone_numbers) != PHONE_DIGITS:
        raise ValueError('Telefone deve ter 11 dígitos (com DDD)')

    # Validar DDD brasileiro (11 a 99)
    ddd = int(phone_numbers[:2])
    if ddd < MIN_DDD or ddd > MAX_DDD:
        raise ValueError('DDD inválido')

    return phone_numbers


PhoneValidate = Annotated[str, AfterValidator(validate_phone)]


StrongPassword = Annotated[
    str,
    Field(min_length=8, max_length=128),
    AfterValidator(validate_strong_password),
]


class UserRole(str, Enum):
    USER = 'user'
    USER_PREMIUM = 'user_premium'
    ADMIN = 'admin'


class UserPublic(BaseModel):
    id: UUID
    username: str = Field(min_length=3)
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserSubscription(BaseModel):
    id: UUID
    username: str = Field(min_length=3)
    email: EmailStr
    phone: str
    subscription_active: bool
    subscription_expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: StrongPassword
    phone: PhoneValidate

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]
