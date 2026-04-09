from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import AppointmentStatus, RoleEnum


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    phone_number: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8)


class ClinicBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class ClinicCreate(ClinicBase):
    pass


class ClinicOut(ClinicBase):
    id: int
    api_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(min_length=7, max_length=20)
    role: RoleEnum = RoleEnum.staff


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserOut(UserBase):
    id: int
    clinic_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    specialty: str = Field(min_length=2, max_length=120)


class DoctorCreate(DoctorBase):
    pass


class DoctorOut(DoctorBase):
    id: int
    clinic_id: int

    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_name: str = Field(min_length=2, max_length=120)
    patient_phone: str = Field(min_length=7, max_length=20)
    appointment_time: datetime
    reason: str | None = Field(default=None, max_length=1000)


class AppointmentCancel(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)


class AppointmentOut(BaseModel):
    id: int
    clinic_id: int
    doctor_id: int
    created_by_user_id: int | None
    patient_name: str
    patient_phone: str
    appointment_time: datetime
    reason: str | None
    status: AppointmentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VapiScheduleRequest(BaseModel):
    clinic_api_key: str
    doctor_id: int
    patient_name: str
    patient_phone: str
    appointment_time: datetime
    reason: str | None = None


class VapiCancelRequest(BaseModel):
    clinic_api_key: str
    appointment_id: int
    reason: str | None = None
