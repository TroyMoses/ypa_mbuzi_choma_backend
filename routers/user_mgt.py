# routers/user_mgt.py
import os
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from routers.schemas import (
    LoginRequest,
    LoginResponse,
    LoginUser,
    RegisterRequest,
    VerifyResponse,
)
from database import get_db
from models import User
from dotenv import load_dotenv

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter(prefix="/auth", tags=["auth"])


# -----------------------
# LOGIN
# -----------------------
@router.post("/login", response_model=LoginResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user.id),
        "exp": expire,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "is_admin": user.is_admin,
        },
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return LoginResponse(token=token, user=LoginUser.from_orm(user))


# -----------------------
# REGISTER
# -----------------------
@router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(request.password)
    new_user = User(
        username=request.first_name.lower().replace(
            " ", "_"
        ),  # generate username if not provided
        email=request.email,
        password_hash=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        role="admin",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role,
            "is_admin": new_user.is_admin,
        },
    }


# -----------------------
# VERIFY TOKEN
# -----------------------
@router.get("/verify", response_model=VerifyResponse)
def verify_token(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_data = payload.get("user")
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
