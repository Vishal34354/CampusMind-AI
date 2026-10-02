from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(self, data: UserRegister) -> User:
        existing_user = self.repository.get_by_email(data.email)

        if existing_user:
            raise ValueError("Email is already registered")

        is_admin = False
        role = "user"
        if settings.ADMIN_EMAIL and data.email.strip().lower() == settings.ADMIN_EMAIL.strip().lower():
            is_admin = True
            role = "admin"

        user = self.repository.create(
            full_name=data.full_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=role,
            is_admin=is_admin,
        )

        return user

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:
        user = self.repository.get_by_email(email)

        if user is None:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        if not user.is_active:
            return None

        return user