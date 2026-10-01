from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.security import hash_password
from app.models.user import User
from app.schema.user import UserCreate, UserUpdate


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

def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    for field in ("email", "username", "phoneNo"):
        value = update_data.get(field)
        if field not in update_data:
            continue
        if value is None:
            if field == "phoneNo":
                user.phoneNo = None
            continue

        existing = db.query(User).filter(
            getattr(User, field) == value,
            User.id != user_id,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"{field} is already in use.")
        setattr(user, field, value)

    if update_data.get("password") is not None:
        user.password = hash_password(update_data["password"])

    db.commit()
    db.refresh(user)
    return user