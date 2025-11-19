import uuid
from http import HTTPStatus

from Backend.models.MetasSchemas import MetaPublic


def test_create_meta(client, user, token_admin):
    response = client.post(
        '/metas/',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={
            'name': 'Carro Novo',
            'value': 20000,
            'value_actual': 10,
            'time': '2026-09-20',
            'user_id': str(user.id),
        },
    )

    id = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': id['id'],
        'name': 'Carro Novo',
        'value': '20000.00',
        'value_actual': '10.00',
        'time': '2026-09-20',
        'user_id': str(user.id),
    }


def test_create_meta_not_permissions(client, user, token):
    response = client.post(
        '/metas/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Carro Novo',
            'value': 20000,
            'value_actual': 10,
            'time': '2026-09-20',
            'user_id': str(user.id),
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}


def test_read_metas(client, meta, token_admin):
    meta_schema = MetaPublic.model_validate(meta).model_dump()
    response = client.get(
        '/metas/', headers={'Authorization': f'Bearer {token_admin}'}
    )

    for item in meta_schema:
        meta_schema[f'{item}'] = str(meta_schema[f'{item}'])

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'metas': [meta_schema]}


def test_update_meta(client, meta, user, token_admin):
    response = client.put(
        f'/metas/{meta.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={
            'name': 'Carro Novo',
            'value': 20000,
            'value_actual': 10,
            'time': '2026-09-20',
        },
    )

    id = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': id['id'],
        'name': 'Carro Novo',
        'value': '20000.00',
        'value_actual': '10.00',
        'time': '2026-09-20',
        'user_id': str(user.id),
    }


def test_update_meta_not_found(client, meta, token_admin):
    response = client.put(
        f'/metas/{str(uuid.uuid4())}',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={
            'name': 'Carro Novo',
            'value': 20000,
            'value_actual': 10,
            'time': '2026-09-20',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Meta not found'}


def test_update_meta_not_permission(client, meta, token):
    response = client.put(
        f'/metas/{meta.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Carro Novo',
            'value': 20000,
            'value_actual': 10,
            'time': '2026-09-20',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}


def test_delete_meta(client, meta, token_admin):
    response = client.delete(
        f'/metas/{meta.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Meta deleted'}


def test_delete_gasto_not_permission(client, meta, token):
    response = client.delete(
        f'/metas/{meta.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}
