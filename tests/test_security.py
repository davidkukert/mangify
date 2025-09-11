import pytest
from pwdlib.exceptions import UnknownHashError

from src.security import (  # ajuste o import conforme seu projeto
    get_password_hash,
    verify_password,
)


def test_get_password_hash_returns_different_from_plain():
    password = 'minha_senha_super_segura'
    hashed = get_password_hash(password)

    assert isinstance(hashed, str)
    assert (
        hashed != password
    )  # o hash nunca deve ser igual à senha em texto puro


def test_verify_password_success():
    password = 'senha123'
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    password = 'senha123'
    hashed = get_password_hash(password)

    assert verify_password('senha_errada', hashed) is False


def test_verify_password_with_invalid_hash():
    password = 'senha123'
    fake_hash = 'invalid_hash_format'

    # deve retornar False ou levantar exceção dependendo do backend do pwdlib
    with pytest.raises(
        UnknownHashError,
        match=(
            "This hash can't be identified. Make sure it's valid and that "
            'its corresponding hasher is enabled.'
        ),
    ):
        verify_password(password, fake_hash)
