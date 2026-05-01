from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import error_payload
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.repositories.user_repository import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "UNAUTHORIZED", "message": "Token ausente ou invalido"},
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
    ) -> User:
    
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except JWTError as exc:
        raise credentials_exception() from exc

    if not user_id:
        raise credentials_exception()

    user = user_repository.get(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception()
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_payload("FORBIDDEN", "Usuario sem permissao de administrador")["detail"],
        )
    return current_user
