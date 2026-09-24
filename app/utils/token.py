from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from app.core.env_data import SALT, JWT_SECRET_KEY
import jwt
from datetime import datetime, timedelta, timezone
from app.core.env_data import JWT_SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, JWT_ACCESS_TOKEN_EXPIRE_MINUTES

serializer = URLSafeTimedSerializer(JWT_SECRET_KEY)


def generate_verification_token(email: str) -> str:
    return serializer.dumps(email, salt=SALT)


def verify_verification_token(token: str, max_age_seconds: int = 3600) -> str:
    """
    Returns the email if valid, raises ValueError if expired/invalid.
    """
    try:
        email = serializer.loads(token, salt=SALT, max_age=max_age_seconds)
    except SignatureExpired:
        raise ValueError("Verification link has expired.")
    except BadSignature:
        raise ValueError("Invalid verification token.")
    return email

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token.")