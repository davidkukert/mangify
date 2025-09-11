from http import HTTPStatus


def test_index_root(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Bem vindo ao Mangify!'}
