import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_admin_user
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import (
    AdminUserListResponse,
    AdminUserResponse,
    UserStatusUpdate,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/users",
    response_model=AdminUserListResponse,
)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by name or email"),
    status_filter: str | None = Query(
        None, description="Filter by status: active, inactive, all"
    ),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)

    items, total = repository.get_users_paginated(
        search=search,
        status_filter=status_filter,
        page=page,
        limit=limit,
    )

    pages = math.ceil(total / limit) if total > 0 else 1

    return AdminUserListResponse(
        items=[AdminUserResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse,
)
def get_user_detail(
    user_id: UUID,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)

    user = repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    items, _ = repository.get_users_paginated(
        search=user.email,
        page=1,
        limit=1,
    )
    materials_count = items[0]["materials_count"] if items else 0

    return AdminUserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        materials_count=materials_count,
    )


@router.patch(
    "/users/{user_id}/status",
    response_model=AdminUserResponse,
)
def update_user_status(
    user_id: UUID,
    data: UserStatusUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)

    target_user = repository.get_by_id(user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if target_user.id == current_admin.id and not data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own administrator account",
        )

    if (target_user.is_admin or target_user.role == "admin") and not data.is_active:
        active_admins = repository.count_active_admins()
        if active_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last active administrator account",
            )

    updated_user = repository.update_status(target_user, data.is_active)

    items, _ = repository.get_users_paginated(
        search=updated_user.email,
        page=1,
        limit=1,
    )
    materials_count = items[0]["materials_count"] if items else 0

    return AdminUserResponse(
        id=updated_user.id,
        full_name=updated_user.full_name,
        email=updated_user.email,
        role=updated_user.role,
        is_admin=updated_user.is_admin,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        materials_count=materials_count,
    )
