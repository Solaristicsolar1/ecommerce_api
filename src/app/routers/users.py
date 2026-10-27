import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.models.user import User
from app.utils.auth import hash_password
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["Users"])
@router.get("", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    statement = select(User)
    users = db.scalars(statement).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: uuid.UUID, db: Session=Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@router.post("", response_model=UserResponse)
def post_user(user: UserCreate, db: Session = Depends(get_db)):
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

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: uuid.UUID, user_data: UserUpdate, db: Session=Depends(get_db)):
    user = db.get(User, user_id)

    # 2. Check whether the user exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 3. Extract only the fields supplied by the client
    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    # 4. Validate fields that cannot be NULL or empty
    if "full_name" in update_data:
        full_name = update_data["full_name"]

        if full_name is None or not full_name.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Full name cannot be empty",
            )

        update_data["full_name"] = full_name.strip()

    if "email" in update_data and update_data["email"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email cannot be null",
        )

    # 5. Apply the changes to the SQLAlchemy object
    for field, value in update_data.items():
        setattr(user, field, value)

    # 6. Save the changes to PostgreSQL
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Update conflicts with existing data or a database constraint",
        )

    # 7. Reload and return the updated user
    db.refresh(user)

    return user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    # 1. Find the user
    user = db.get(User, user_id)

    # 2. Check whether the user exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 3. Delete and commit
    try:
        db.delete(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted because related records or database constraints prevent it",
        )

    return None
    
    

