from http import HTTPStatus

from backend.models.CategoriaSchema import CategoriaPublic


def test_create_categoria(client, token_admin):
    response = client.post(
        '/categorias/',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={'name': 'Alimentação'},
    )

    id = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'Alimentação',
        'id': id['id'],
    }


def test_create_categoria_integrity_error(client, categoria, token_admin):
    response = client.post(
        '/categorias/',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={'name': 'Alimentação'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Ja existe uma categoria registrada com esse nome'
    }


def test_create_categoria_not_permissions(client, token):
    response = client.post(
        '/categorias/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Alimentação'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}


def test_read_categorias(client, categoria, token_admin):
    categoria_schema = CategoriaPublic.model_validate(categoria).model_dump()
    response = client.get(
        '/categorias/', headers={'Authorization': f'Bearer {token_admin}'}
    )

    for item in categoria_schema:
        categoria_schema[f'{item}'] = str(categoria_schema[f'{item}'])

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'categorias': [categoria_schema]}


def test_update_categoria(client, categoria, token_admin):
    response = client.put(
        f'/categorias/{categoria.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={'name': 'Moradia'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'name': 'Moradia', 'id': str(categoria.id)}


def test_update_categoria_integrity_error(client, categoria, token_admin):
    client.post(
        '/categorias/',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={'name': 'Moradia'},
    )

    response = client.put(
        f'/categorias/{categoria.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={'name': 'Moradia'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Categoria already exist'}


def test_update_categoria_not_permission(client, categoria, token):
    response = client.put(
        f'/categorias/{categoria.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Moradia'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}


def test_delete_categoria(client, categoria, token_admin):
    response = client.delete(
        f'/categorias/{categoria.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Categoria deleted'}


def test_delete_categoria_not_permission(client, categoria, token):
    response = client.delete(
        f'/categorias/{categoria.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Insufficient permissions'}
