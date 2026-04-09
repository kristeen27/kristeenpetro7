import logging

from app.models import Appointment, AppointmentStatus

logger = logging.getLogger(__name__)


class WhatsAppNotificationService:
    """Meta WhatsApp API ready service wrapper.

    In production, replace the logger call with requests to Graph API using
    app.core.config settings tokens.
    """

    @staticmethod
    def send_appointment_event(appointment: Appointment) -> None:
        if appointment.status == AppointmentStatus.scheduled:
            template = "appointment_booked"
        else:
            template = "appointment_canceled"
        logger.info(
            "WhatsApp event=%s clinic_id=%s patient_phone=%s appointment_id=%s",
            template,
            appointment.clinic_id,
            appointment.patient_phone,
            appointment.id,
        )
