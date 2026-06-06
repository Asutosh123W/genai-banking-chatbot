from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from sqlalchemy.orm import Session

from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
from database.database import get_db
from database.models import User
from models.auth_models import RegisterRequest
from services.auth_service import (
    hash_password
)
from models.auth_models import (
    LoginRequest,
    TokenResponse
)

from services.auth_service import (
    verify_password,
    create_access_token,
    verify_token
)

from services.token_service import (
    get_current_email
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()

@router.post("/register")
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:

        return {
            "message":
            "Email already registered"
        }

    user = User(
    username=request.username,
    email=request.email,
    password_hash=hash_password(
        request.password
    )
)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message":
        "User created successfully",
        "user_id":
        user.id
    }

@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:

        return {
            "access_token": "",
            "token_type": "invalid"
        }

    valid_password = verify_password(
        request.password,
        user.password_hash
    )

    if not valid_password:

        return {
            "access_token": "",
            "token_type": "invalid"
        }

    token = create_access_token(
        {
            "sub": user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def current_user(

    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),

    db: Session = Depends(
        get_db
    )

):

    token = credentials.credentials

    email = verify_token(token)

    if not email:

        return {
            "message": "Invalid token"
        }

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        return {
            "message": "User not found"
        }

    return {

        "id": user.id,

        "username":
            user.username,

        "email":
            user.email

    }