from datetime import UTC, datetime, timedelta
from typing import Any
from jose import jwt
from passlib.context import CryptContext
from app.core.config import get_settings

# Serve para verificar e gerar hashes de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    Args:
        plain_password: A senha fornecida pelo usuario.
        hashed_password: O hash da senha armazenado no banco de dados.
    Returns:
        True se a senha fornecida corresponde ao hash armazenado, False caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera um hash da senha fornecida.
    Args:
        password: A senha fornecida pelo usuario.
    Returns:
        O hash da senha.
    """
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str) -> str:
    """
    Cria um token de acesso.
    Args:
        subject: O ID do usuario.
        role: O role do usuario.
    Returns:
        O token de acesso.
    """
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodifica um token de acesso.
    Args:
        token: O token de acesso.
    Returns:
        O payload do token.
    """
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
