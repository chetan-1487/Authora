from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import repository, schema
from .service import get_db
from ..user.service import get_current_user

router = APIRouter(
    tags=["User_Information"]
)

@router.get("/user/info", response_model=schema.UserResponse)
def get_user_info(current_user=Depends(get_current_user)):
    return current_user

@router.put("/update", response_model=schema.UserResponse)
def update_user_info(data: schema.UpdateUserRequest,db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    updated_user = repository.update_user(db, current_user.id, data)
    return updated_user

@router.delete("/delete")
def delete_user_account(db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    repository.delete_user(db, current_user.id)
    return {"msg": "User deleted successfully"}
