import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import DECIMAL, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from Backend.models.UserSchema import UserRole

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        init=False,
    )
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    phone: Mapped[str] = mapped_column(String(11), unique=True)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.USER, nullable=False
    )
    subscription_active: Mapped[bool] = mapped_column(default=False)
    subscription_expires_at: Mapped[datetime] = mapped_column(
        nullable=True, default=None
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, unique=True, init=False
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, unique=True, init=False
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, default=None, init=True, onupdate=func.now()
    )

    gastos: Mapped[list['Gastos']] = relationship(
        init=False, back_populates='user', lazy='selectin'
    )
    metas: Mapped[list['Metas']] = relationship(
        init=False,
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
    )


@table_registry.mapped_as_dataclass
class Gastos:
    __tablename__ = 'gastos'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, init=False
    )
    message: Mapped[str] = mapped_column(String(400))
    value: Mapped[float] = mapped_column(DECIMAL(12, 2))
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('categorias.id')
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, default=None, init=True, onupdate=func.now()
    )

    categoria: Mapped['Categorias'] = relationship(
        init=False, back_populates='gastos', lazy='selectin'
    )
    user: Mapped['User'] = relationship(
        init=False, back_populates='gastos', lazy='selectin'
    )


@table_registry.mapped_as_dataclass
class Categorias:
    __tablename__ = 'categorias'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, init=False
    )
    name: Mapped[str] = mapped_column(String(80), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, default=None, init=True, onupdate=func.now()
    )

    gastos: Mapped['Gastos'] = relationship(
        init=False, back_populates='categoria'
    )


@table_registry.mapped_as_dataclass
class Metas:
    __tablename__ = 'metas'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, init=False
    )
    name: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(DECIMAL(12, 2))
    time: Mapped[date]
    value_actual: Mapped[float] = mapped_column(DECIMAL(12, 2))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, default=None, init=True, onupdate=func.now()
    )

    user: Mapped['User'] = relationship(
        init=False, back_populates='metas', lazy='selectin'
    )
