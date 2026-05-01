from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import user_repository


class AuthService:
    """
    Serviço de autenticação.
    """
    def authenticate(self, db: Session, email: str, password: str) -> User | None:
        """
        Autentica um usuário.
        Args:
            db: A sessão do banco de dados.
            email: O email do usuário.
            password: A senha do usuário.
        Return:
            O usuário autenticado ou None se não encontrado ou inativo.
        """
        user = user_repository.get_by_email(db, email)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_token(self, user: User) -> str:
        """
        Cria um token de acesso.
        Args:
            user: O usuário.
        Return:
            O token de acesso.
        """
        return create_access_token(subject=user.id, role=user.role.value)


auth_service = AuthService()
