from http import HTTPStatus


def test_read_root(client):
    response = client.get('/')

    assert response.json() == {'message': 'Hello World'}
    assert response.status_code == HTTPStatus.OK
