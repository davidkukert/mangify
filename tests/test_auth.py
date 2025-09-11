from http import HTTPStatus

from freezegun import freeze_time
from jwt import encode
from ulid import ulid

from src.schemas.users import UserType
from src.settings import settings


def test_login_for_access_token(client, user: UserType):
    response = client.post(
        '/auth/token',
        data={'username': user['username'], 'password': 'testpassword'},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'accessToken' in data
    assert data['tokenType'] == 'bearer'


def test_login_for_access_token_invalid_credentials(client):
    response = client.post(
        '/auth/token',
        data={'username': 'invaliduser', 'password': 'wrongpassword'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Nome de usuário ou senha incorretos'}


def test_refresh_access_token(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/auth/refresh', headers=headers)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'accessToken' in data
    assert data['tokenType'] == 'bearer'
    assert data['accessToken'] != token


def test_token_expired_after_time(client, user: UserType):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user['username'], 'password': 'testpassword'},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['accessToken']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.get(
            '/auth/me',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Não foi possível validar as credenciais'
        }


def test_token_wrong_password(client, user: UserType):
    response = client.post(
        '/auth/token',
        data={'username': user['username'], 'password': 'wrong_password'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Nome de usuário ou senha incorretos'}


def test_token_expired_dont_refresh(client, user: UserType):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user['username'], 'password': 'testpassword'},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['accessToken']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.post(
            '/auth/refresh',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Não foi possível validar as credenciais'
        }


def test_get_me(client, token, user: UserType):
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/auth/me', headers=headers)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'data' in data
    assert data['data']['id'] == user['_id']
    assert data['data']['username'] == user['username']
    assert 'password' not in data['data']
    assert 'createdAt' in data['data']
    assert 'updatedAt' in data['data']


def test_token_subject_missing(client):
    token = encode({}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/auth/me', headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Não foi possível validar as credenciais'
    }


def test_token_user_not_found(client):
    token = encode(
        {'sub': ulid()}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/auth/me', headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Não foi possível validar as credenciais'
    }


def test_no_token_provided(client):
    response = client.get('/auth/me')
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_malformed_token(client):
    headers = {'Authorization': 'Bearer malformed.token.here'}
    response = client.get('/auth/me', headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Não foi possível validar as credenciais'
    }
