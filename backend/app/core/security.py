from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
import jwt
from app.core.config import settings
import hashlib
import hmac

password_hash = PasswordHash.recommended()

def hash_password(password : str) -> str:
    return password_hash.hash(password)

def verify_password(password : str , hashed_password : str) -> bool:
    return password_hash.verify(
        password,
        hashed_password
    )

def create_access_token(data : dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp" : expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

def decode_access_token(token : str):
    try : 
        payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

        return payload

    except jwt.InvalidTokenError:
        return None

def create_otp_digest(
    otp: str,
    user_id: int,
    purpose: str
) -> str:
    message = f"{purpose}:{user_id}:{otp}".encode()

    return hmac.new(
        settings.OTP_SECRET.encode(),
        message,
        hashlib.sha256
    ).hexdigest()

def verify_otp(
    otp: str,
    user_id: int,
    stored_digest: str,
    purpose: str
) -> bool:
    expected_digest = create_otp_digest(
        otp,
        user_id,
        purpose
    )

    return hmac.compare_digest(
        expected_digest,
        stored_digest
    )