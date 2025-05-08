from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.orm import Session
from . import repository  # assuming you have repository.py for DB queries
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_jwt_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return user_id
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed")


# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     user_id = verify_jwt_token(token)
#     user = repository.get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    user_id = verify_jwt_token(token)
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
