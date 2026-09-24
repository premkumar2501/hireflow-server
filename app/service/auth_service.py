
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schema.token import RefreshRequest, TokenResponse
from app.schema.user import LoginRequest, RegisterResponse, UserCreate, UserResponse, VerifyUser
from app.utils.token import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_verification_token,
    verify_verification_token,
)


def get_exist_user(user_email: str, db: Session):
    return db.query(User).filter(User.email == user_email).first()


def register(db: Session, user: UserCreate) -> RegisterResponse:
    exist_user = db.query(User).filter((User.email == user.email) | (User.username == user.username)).first()
    if exist_user:
        raise HTTPException(status_code=400, detail="User with this email or username already exists.")

    timestamp = datetime.now(timezone.utc)
    hashed_password = hash_password(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
        phoneNo=user.phoneNo,
        created_at=timestamp,
        updated_at=timestamp,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = generate_verification_token(new_user.email)
    return RegisterResponse(user=new_user, verification_token=token)

def verify_user(user: VerifyUser, db: Session) -> UserResponse:
    user_email = verify_verification_token(user.token)
    if user_email:
        user_detail = get_exist_user(user_email, db)
        user_detail.is_varify = True
        db.commit()
        db.refresh(user_detail)
        return user_detail
        
def login(credentials: LoginRequest, db: Session):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect email or password."},
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    
def refresh_token(payload: RefreshRequest, db: Session):
    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": str(e)},
        )

    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Token is not a refresh token."},
        )

    user_id = int(decoded["sub"])
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found."},
        )

    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)  # optional: rotate refresh token too

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)  
