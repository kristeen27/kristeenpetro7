from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Appointment, AppointmentStatus, User
from app.schemas import AppointmentCancel, AppointmentCreate, AppointmentOut
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def schedule_appointment(
    payload: AppointmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        return AppointmentService.schedule(db=db, clinic_id=current_user.clinic_id, payload=payload, created_by=current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(
    appointment_id: int,
    payload: AppointmentCancel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.clinic_id == current_user.clinic_id)
        .first()
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status == AppointmentStatus.canceled:
        raise HTTPException(status_code=400, detail="Appointment already canceled")
    return AppointmentService.cancel(db=db, appointment=appointment, reason=payload.reason)


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    doctor_id: int | None = Query(default=None),
    status_filter: AppointmentStatus | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Appointment).filter(Appointment.clinic_id == current_user.clinic_id)

    if doctor_id is not None:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if date_from is not None:
        query = query.filter(Appointment.appointment_time >= date_from)
    if date_to is not None:
        query = query.filter(Appointment.appointment_time <= date_to)
    if status_filter is not None:
        query = query.filter(Appointment.status == status_filter)

    return query.order_by(Appointment.appointment_time.asc()).all()
