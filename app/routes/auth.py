from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schema.user import RegisterResponse, UserCreate, UserResponse, VerifyUser, LoginRequest
from app.schema.token import RefreshRequest
from app.service import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"])


@router.post("/register", summary="Register a new user", response_model=RegisterResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> RegisterResponse:
    return auth_service.register(db, user)

@router.post("/login", summary="Login")
def login_user(login_req: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(login_req, db)

@router.post("/refresh-token", summary="Get tokens")
def get_tokens(token_req: RefreshRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_token(token_req, db)


@router.post("/verify-user", summary="User verify")
def verify_user(user: VerifyUser, db: Session = Depends(get_db)) -> UserResponse:
    return auth_service.verify_user(user, db)