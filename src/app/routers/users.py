from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
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