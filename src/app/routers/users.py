from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app.database import get_db
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.utils.auth import hash_password
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["Users"])
@router.get("/users", response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    statement = select(User)
    users = db.scalars(statement).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, db: Session=Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@router.post("/users", response_model=UserResponse)
async def post_user(user: UserCreate, db: Session = Depends(get_db)):
    create_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        phone=user.phone,
    )
    try:
        db.add(create_user)
        db.commit()
        db.refresh(create_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email or another conflicting unique value already exists.",
        )
    return create_user

@router.patch("users/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, db: Session=Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    

