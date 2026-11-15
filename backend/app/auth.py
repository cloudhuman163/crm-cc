from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import get_db
from .models import User

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_TTL = timedelta(hours=12)

router = APIRouter(prefix="/auth", tags=["auth"])

class UserIn(BaseModel):
    username: str
    password: str
    full_name: str = ""

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

@router.post("/register", response_model=TokenOut)
def register(data: UserIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Пользователь уже существует")
    user = User(
        username=data.username,
        password_hash=pwd.hash(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=_token(user.username), username=user.username)

@router.post("/login", response_model=TokenOut)
def login(data: UserIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not pwd.verify(data.password, user.password_hash):
        raise HTTPException(401, "Неверный логин или пароль")
    return TokenOut(access_token=_token(user.username), username=user.username)

def _token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + TOKEN_TTL,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
