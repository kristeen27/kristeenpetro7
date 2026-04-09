from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, AppointmentStatus, Clinic
from app.schemas import AppointmentCreate, AppointmentOut, VapiCancelRequest, VapiScheduleRequest
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/vapi", tags=["vapi-webhooks"])


def _get_clinic_by_api_key(db: Session, clinic_api_key: str) -> Clinic:
    clinic = db.query(Clinic).filter(Clinic.api_key == clinic_api_key).first()
    if not clinic:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid clinic API key")
    return clinic


@router.post("/schedule", response_model=AppointmentOut)
def vapi_schedule(payload: VapiScheduleRequest, db: Session = Depends(get_db)):
    clinic = _get_clinic_by_api_key(db=db, clinic_api_key=payload.clinic_api_key)
    appointment_payload = AppointmentCreate(
        doctor_id=payload.doctor_id,
        patient_name=payload.patient_name,
        patient_phone=payload.patient_phone,
        appointment_time=payload.appointment_time,
        reason=payload.reason,
    )
    try:
        return AppointmentService.schedule(db=db, clinic_id=clinic.id, payload=appointment_payload, created_by=None)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/cancel", response_model=AppointmentOut)
def vapi_cancel(payload: VapiCancelRequest, db: Session = Depends(get_db)):
    clinic = _get_clinic_by_api_key(db=db, clinic_api_key=payload.clinic_api_key)
    appointment = (
        db.query(Appointment).filter(Appointment.id == payload.appointment_id, Appointment.clinic_id == clinic.id).first()
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status == AppointmentStatus.canceled:
        raise HTTPException(status_code=400, detail="Appointment already canceled")

    return AppointmentService.cancel(db=db, appointment=appointment, reason=payload.reason)
