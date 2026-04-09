from fastapi import FastAPI

from app.database import Base, engine
from app.routers import appointments, clinics, doctors, users, vapi

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital Appointment SaaS", version="1.0.0")

app.include_router(users.router)
app.include_router(clinics.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(vapi.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
