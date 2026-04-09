from sqlalchemy.orm import Session

from app.models import Appointment, AppointmentStatus, Doctor, User
from app.schemas import AppointmentCreate
from app.services.notification_service import WhatsAppNotificationService


class AppointmentService:
    @staticmethod
    def schedule(db: Session, clinic_id: int, payload: AppointmentCreate, created_by: User | None) -> Appointment:
        doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id, Doctor.clinic_id == clinic_id).first()
        if not doctor:
            raise ValueError("Doctor not found for this clinic")

        appointment = Appointment(
            clinic_id=clinic_id,
            doctor_id=payload.doctor_id,
            created_by_user_id=created_by.id if created_by else None,
            patient_name=payload.patient_name,
            patient_phone=payload.patient_phone,
            appointment_time=payload.appointment_time,
            reason=payload.reason,
            status=AppointmentStatus.scheduled,
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        WhatsAppNotificationService.send_appointment_event(appointment)
        return appointment

    @staticmethod
    def cancel(db: Session, appointment: Appointment, reason: str | None = None) -> Appointment:
        appointment.status = AppointmentStatus.canceled
        if reason:
            appointment.reason = reason
        db.commit()
        db.refresh(appointment)
        WhatsAppNotificationService.send_appointment_event(appointment)
        return appointment
