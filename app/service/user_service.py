from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.schema.user import UserCreate


def create_user(db: Session, user_data: UserCreate) -> User:
    existing = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists.",
        )

    new_user = User(email=user_data.email, username=user_data.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def delete_user(db: Session, user_id: int): 
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}