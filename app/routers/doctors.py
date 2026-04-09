from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Doctor, User
from app.schemas import DoctorCreate, DoctorOut

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create doctors")
    doctor = Doctor(clinic_id=current_user.clinic_id, full_name=payload.full_name, specialty=payload.specialty)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("", response_model=list[DoctorOut])
def list_doctors(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Doctor).filter(Doctor.clinic_id == current_user.clinic_id).order_by(Doctor.full_name).all()
