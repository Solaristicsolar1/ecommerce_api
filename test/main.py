from fastapi import Depends, HTTPException, Response, status, FastAPI
# import uuid
import uvicorn
from typing import Annotated
from sqlalchemy import select
from model import User
from database import engine, Base, get_db 
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

class UserBody(BaseModel):
    name: str = Field(max_length=50, min_length=2)
    email: EmailStr

class UserUpdate(BaseModel):
    name: Annotated[str, Field(max_length=50, min_length=2)] | None = None
    email: Annotated[EmailStr, Field()] | None = None

app = FastAPI()

Base.metadata.create_all(bind=engine)      

@app.get("/users")
async def read_users(db: Session = Depends(get_db)):
    statement = select(User)
    user = db.scalars(statement).all()
    return user

@app.post("/users")
async def add_new_user(user: UserBody, db: Session = Depends(get_db)):
    new_user = User(
        name = user.name,
        email = user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


@app.patch("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user   

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)