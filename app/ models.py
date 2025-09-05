from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# User Models
class UserSignUp(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Appointment Models
class AppointmentCreate(BaseModel):
    doctor_id: str
    date: str  # Format: YYYY-MM-DD
    time_slot: str  # Format: HH:MM-HH:MM

class AppointmentUpdate(BaseModel):
    date: Optional[str] = None
    time_slot: Optional[str] = None

class AppointmentResponse(BaseModel):
    success: bool
    message: str
    appointment_id: Optional[str] = None

class Appointment(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    doctor_id: str
    date: str
    time_slot: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

# Doctor Model (for reference)
class Doctor(BaseModel):
    id: str = Field(alias="_id")
    name: str
    specialty: str
    available_slots: list[str]
    
    class Config:
        populate_by_name = True