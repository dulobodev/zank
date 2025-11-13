import uuid
from datetime import date

import factory
import pytest_asyncio

from backend.middleware.security import get_password_hash
from backend.models.models import Categorias, Gastos, Metas, User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    phone = factory.Sequence(lambda n: f'199999{n % 10000:05d}')


class CategoriaFactory(factory.Factory):
    class Meta:
        model = Categorias

    name = factory.Iterator(['Alimentação', 'Moradia', 'Games', 'Transporte'])


class GastoFactory(factory.Factory):
    class Meta:
        model = Gastos

    message = factory.Sequence(lambda n: f'Mensagem{n}')
    value = factory.Sequence(lambda n: (f'{n + 1}{n + 1}.00'))
    categoria_id = factory.LazyFunction(uuid.uuid4)  # Valor padrão
    user_id = factory.LazyFunction(uuid.uuid4)  # Valor padrão


class MetaFactory(factory.Factory):
    class Meta:
        model = Metas

    name = factory.Sequence(lambda n: f'Mensagem{n}')
    value = factory.Sequence(lambda n: (f'{n + 1}{n + 1}.00'))
    time = factory.LazyFunction(date.today)
    value_actual = factory.Sequence(lambda n: (f'{n + 2}{n + 2}.00'))
    user_id = factory.LazyFunction(uuid.uuid4)


@pytest_asyncio.fixture
async def user(session):
    password = 'Test@test1'
    user = UserFactory(
        password=get_password_hash(password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def admin(session):
    password = 'Test@test1'
    user = UserFactory(
        password=get_password_hash(password), role='ADMIN', phone='19999999421'
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'Test@test1'
    user = UserFactory(
        password=get_password_hash(password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def categoria(session):
    categoria = CategoriaFactory()

    session.add(categoria)
    await session.commit()
    await session.refresh(categoria)

    return categoria


@pytest_asyncio.fixture
async def other_categoria(session):
    categoria = CategoriaFactory()

    session.add(categoria)
    await session.commit()
    await session.refresh(categoria)

    return categoria


@pytest_asyncio.fixture
async def gasto(session, user, categoria):
    gasto = GastoFactory(user_id=user.id, categoria_id=categoria.id)

    session.add(gasto)
    await session.commit()
    await session.refresh(gasto)

    return gasto


@pytest_asyncio.fixture
async def other_gasto(session):
    gasto = GastoFactory()

    session.add(gasto)
    await session.commit()
    await session.refresh(gasto)

    return gasto


@pytest_asyncio.fixture
async def meta(session, user):
    meta = MetaFactory(user_id=user.id)

    session.add(meta)
    await session.commit()
    await session.refresh(meta)

    return meta
