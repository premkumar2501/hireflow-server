from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.dependencies import get_db
import jwt
from app.core.env_data import JWT_SECRET_KEY, ALGORITHM
from app.models.user import User

bearer = HTTPBearer()

def user_auth(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise unauthorized
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise unauthorized
    return user
    