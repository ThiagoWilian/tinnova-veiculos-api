from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User, UserRole


class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def get(self, db: Session, user_id: str) -> User | None:
        return db.get(User, user_id)

    def create(self, db: Session, email: str, password: str, role: UserRole) -> User:
        user = User(email=email, hashed_password=get_password_hash(password), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository()
