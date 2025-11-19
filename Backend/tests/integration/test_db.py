from dataclasses import asdict

import pytest
from sqlalchemy import select

from Backend.models.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='teste',
            email='teste@teste.com',
            password='teste123',
            phone='19999999999',
            role='user',
            subscription_active=False,
            subscription_expires_at=None,
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'teste')
        )

    assert asdict(user) == {
        'id': user.id,
        'username': 'teste',
        'email': 'teste@teste.com',
        'password': 'teste123',
        'created_at': time,
        'update_at': None,
        'phone': '19999999999',
        'role': 'user',
        'subscription_active': False,
        'subscription_expires_at': None,
        'gastos': [],
        'metas': [],
    }
