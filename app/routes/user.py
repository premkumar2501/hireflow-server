from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schema.user import UserCreate, UserResponse, UserUpdate
from app.dependencies import get_db
from app.service import user_service
from app.middleware.user_auth import require_roles, user_auth
from app.models.user import User
from app.utils.enum import UserRole

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/create", summary="Create a new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    return user_service.create_user(db, user)

@router.get("/{user_id}",  summary="Get a user by ID", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    return user_service.get_user_by_id(db, user_id)

@router.patch("/{user_id}", response_model=UserResponse, summary="Update a user by ID")
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_auth),
) -> UserResponse:
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user_service.update_user(db, user_id, user)

@router.delete("/{user_id}", dependencies=[Depends(require_roles(UserRole.ADMIN))], summary="Delete a user by ID")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.delete_user(db, user_id)
   