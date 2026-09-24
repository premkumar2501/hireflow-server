from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schema.user import UserCreate, UserResponse
from app.dependencies import get_db
from app.service import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/create", summary="Create a new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    return user_service.create_user(db, user)

@router.delete("/{user_id}", summary="Delete a user by ID")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.delete_user(db, user_id)
   