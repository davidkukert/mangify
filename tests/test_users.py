from http import HTTPStatus

import pytest
from ulid import ulid

from src.schemas.users import UserCreateInput, UserType, UserUpdateInput


@pytest.fixture
def user_data():
    return UserCreateInput(username='testuser', password='testpassword')


def test_index_users(client):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'data': []}


def test_create_user(client, user_data):
    response = client.post('/users/', json=user_data.model_dump())
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário criado!'}


def test_create_existing_user(client, user: UserType):
    response = client.post(
        '/users/',
        json=UserCreateInput(
            username=user['username'], password='testpassword'
        ).model_dump(),
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username não esta disponível!'}


def test_show_user(client, user: UserType):
    response = client.get(f'/users/{user["_id"]}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'data': {
            'id': user['_id'],
            'username': user['username'],
            'createdAt': user['created_at'].isoformat(),
            'updatedAt': user['updated_at'].isoformat(),
        }
    }


def test_show_nonexistent_user(client):
    response = client.get(f'/users/{ulid()}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_update_user(client, user: UserType):
    new_username = 'updateduser'
    response_update = client.put(
        f'/users/{user["_id"]}',
        json=UserUpdateInput(username=new_username).model_dump(),
    )
    assert response_update.status_code == HTTPStatus.OK
    assert response_update.json() == {'message': 'Usuário atualizado!'}

    response = client.get(f'/users/{user["_id"]}')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['data']['username'] == new_username


def test_update_nonexistent_user(client):
    response = client.put(
        f'/users/{ulid()}',
        json=UserUpdateInput(username='nonexistentuser').model_dump(),
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado!'}


def test_update_user_to_existing_username(client, user: UserType):
    # Create another user
    response = client.post(
        '/users/',
        json=dict(username='anotheruser', password='password'),
    )
    assert response.status_code == HTTPStatus.OK

    # Attempt to update the first user to the second user's username
    response = client.put(
        f'/users/{user["_id"]}',
        json=UserUpdateInput(username='anotheruser').model_dump(),
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username não esta disponível!'}


def test_update_user_with_some_password(client, user: UserType):
    response = client.put(
        f'/users/{user["_id"]}',
        json=dict(password='testpassword'),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'A nova senha não pode ser igual a senha atual!'
    }


def test_update_user_nothing_changed(client, user: UserType):
    response = client.put(
        f'/users/{user["_id"]}',
        json=UserUpdateInput(username=user['username']).model_dump(),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Nada a ser atualizado!'}


def test_delete_user(client, user: UserType):
    response = client.delete(f'/users/{user["_id"]}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário deletado!'}

    # Verify user is deleted
    response = client.get(f'/users/{user["_id"]}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_delete_nonexistent_user(client):
    response = client.delete(f'/users/{ulid()}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado!'}
