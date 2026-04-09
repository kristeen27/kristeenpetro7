from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_clinic_by_api_key, get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import Clinic, User
from app.schemas import LoginRequest, Token, UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    clinic: Clinic = Depends(get_current_clinic_by_api_key),
    db: Session = Depends(get_db),
):
    exists = db.query(User).filter(User.clinic_id == clinic.id, User.phone_number == payload.phone_number).first()
    if exists:
        raise HTTPException(status_code=400, detail="User already exists in this clinic")

    user = User(
        clinic_id=clinic.id,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, clinic: Clinic = Depends(get_current_clinic_by_api_key), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.clinic_id == clinic.id, User.phone_number == payload.phone_number).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id), clinic_id=user.clinic_id, role=user.role.value)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
