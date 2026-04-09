import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Clinic, User
from app.schemas import ClinicCreate, ClinicOut

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.post("", response_model=ClinicOut, status_code=status.HTTP_201_CREATED)
def create_clinic(payload: ClinicCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    exists = db.query(Clinic).filter(Clinic.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Clinic already exists")

    clinic = Clinic(name=payload.name, api_key=secrets.token_urlsafe(32))
    db.add(clinic)
    db.commit()
    db.refresh(clinic)
    return clinic
