from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.study_material import StudyMaterial
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        return self.db.scalar(statement)

    def get_by_id(self, user_id) -> User | None:
        return self.db.get(User, user_id)

    def create(
        self,
        full_name: str,
        email: str,
        hashed_password: str,
        role: str = "user",
        is_admin: bool = False,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_admin=is_admin,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_users_paginated(
        self,
        search: str | None = None,
        status_filter: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], int]:
        materials_subquery = (
            select(
                StudyMaterial.user_id,
                func.count(StudyMaterial.id).label("materials_count"),
            )
            .group_by(StudyMaterial.user_id)
            .subquery()
        )

        stmt = select(
            User,
            func.coalesce(materials_subquery.c.materials_count, 0).label("materials_count"),
        ).outerjoin(
            materials_subquery, User.id == materials_subquery.c.user_id
        )

        filters = []
        if search and search.strip():
            search_pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    User.full_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                )
            )

        if status_filter:
            status_lower = status_filter.lower().strip()
            if status_lower == "active":
                filters.append(User.is_active.is_(True))
            elif status_lower == "inactive":
                filters.append(User.is_active.is_(False))

        if filters:
            stmt = stmt.where(and_(*filters))

        count_stmt = select(func.count(User.id))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = self.db.scalar(count_stmt) or 0

        offset = (page - 1) * limit
        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)

        results = self.db.execute(stmt).all()

        user_items = []
        for user, mat_count in results:
            user_items.append(
                {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role,
                    "is_admin": user.is_admin,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "materials_count": int(mat_count),
                }
            )

        return user_items, total

    def update_status(self, user: User, is_active: bool) -> User:
        user.is_active = is_active
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def count_active_admins(self) -> int:
        stmt = select(func.count(User.id)).where(
            User.is_active.is_(True),
            or_(User.is_admin.is_(True), User.role == "admin"),
        )
        return self.db.scalar(stmt) or 0

    def promote_to_admin(self, user: User) -> User:
        user.role = "admin"
        user.is_admin = True
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user