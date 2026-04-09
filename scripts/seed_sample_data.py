import secrets
from datetime import datetime, timedelta, timezone

from app.auth import hash_password
from app.database import SessionLocal
from app.models import Clinic, Doctor, RoleEnum, User


def run() -> None:
    db = SessionLocal()
    try:
        clinic = db.query(Clinic).filter(Clinic.name == "City Hospital").first()
        if not clinic:
            clinic = Clinic(name="City Hospital", api_key=secrets.token_urlsafe(32))
            db.add(clinic)
            db.flush()

        admin = (
            db.query(User)
            .filter(User.clinic_id == clinic.id, User.phone_number == "9999999999")
            .first()
        )
        if not admin:
            admin = User(
                clinic_id=clinic.id,
                full_name="Clinic Admin",
                phone_number="9999999999",
                password_hash=hash_password("Admin@12345"),
                role=RoleEnum.admin,
            )
            db.add(admin)

        doctor = db.query(Doctor).filter(Doctor.clinic_id == clinic.id, Doctor.full_name == "Dr. Emily Carter").first()
        if not doctor:
            doctor = Doctor(clinic_id=clinic.id, full_name="Dr. Emily Carter", specialty="Cardiology")
            db.add(doctor)

        db.commit()

        print("Seed complete")
        print(f"Clinic API key: {clinic.api_key}")
        print("Admin login: 9999999999 / Admin@12345")
        print(f"Suggested appointment time: {(datetime.now(timezone.utc) + timedelta(days=1)).isoformat()}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
