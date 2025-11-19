import uuid
from http import HTTPStatus

from Backend.models.GastosSchema import GastosPublic


def test_create_gasto(client, categoria, user, token_admin):
    response = client.post(
        '/gastos/',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={
            'message': 'Livro 10',
            'value': 10,
            'categoria_id': str(categoria.id),
            'user_id': str(user.id),
        },
    )

    json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': json['id'],
        'message': 'Livro 10',
        'value': '10.00',
        'categoria_id': str(categoria.id),
        'user_id': str(user.id),
        'created_at': json['created_at']
    }


def test_create_gasto_not_permissions(client, categoria, user, token):
    response = client.post(
        '/categorias/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'message': 'Livro 10',
            'value': 10,
            'categoria_id': str(categoria.id),
            'user_id': str(user.id),
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}


def test_read_gastos(client, gasto, token_admin):
    gasto_schema = GastosPublic.model_validate(gasto).model_dump(mode='json')
    response = client.get(
        '/gastos/', headers={'Authorization': f'Bearer {token_admin}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'gastos': [gasto_schema]}



def test_update_gasto(client, categoria, gasto, token_admin):
    response = client.put(
        f'/gastos/{gasto.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={
            'message': 'Livro 10',
            'value': 10,
            'categoria_id': str(categoria.id),
        },
    )

    json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': json['id'],
        'message': 'Livro 10',
        'value': '10.00',
        'categoria_id': str(categoria.id),
        'user_id': str(gasto.user_id),
        'created_at': json['created_at']
    }


def test_update_gasto_not_found(client, categoria, gasto, token_admin):
    response = client.put(
        f'/gastos/{str(uuid.uuid4())}',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={
            'message': 'Livro 10',
            'value': 10,
            'categoria_id': str(categoria.id),
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Gasto not found'}


def test_update_gasto_not_found_categoria(client, gasto, token_admin):
    response = client.put(
        f'/gastos/{gasto.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={
            'message': 'Livro 10',
            'value': 10,
            'categoria_id': str(uuid.uuid4()),
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Categoria not found'}


def test_update_gasto_not_permission(client, categoria, gasto, token):
    response = client.put(
        f'/gastos/{gasto.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'message': 'Livro 10',
            'value': 10,
            'categoria_id': str(categoria.id),
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}


def test_delete_gasto(client, gasto, token_admin):
    response = client.delete(
        f'/gastos/{gasto.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Gastos deleted'}


def test_delete_gasto_not_permission(client, gasto, token):
    response = client.delete(
        f'/gastos/{gasto.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}
