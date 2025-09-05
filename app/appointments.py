from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, date
from bson import ObjectId
from typing import List

from app.models import AppointmentCreate, AppointmentUpdate, AppointmentResponse, Appointment, Doctor
from app.database import appointments_collection, doctors_collection, serialize_doc
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/appointments", tags=["Appointments"])

def validate_date_format(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_time_slot_format(time_slot: str) -> bool:
    """Validate time slot format HH:MM-HH:MM"""
    try:
        start_time, end_time = time_slot.split('-')
        datetime.strptime(start_time, "%H:%M")
        datetime.strptime(end_time, "%H:%M")
        return True
    except ValueError:
        return False

def is_appointment_date_future(date_str: str) -> bool:
    """Check if appointment date is in the future"""
    appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    return appointment_date >= date.today()

def is_slot_available(doctor_id: str, appointment_date: str, time_slot: str) -> bool:
    """Check if time slot is available for the doctor on given date"""
    
    # Check if doctor exists and has this time slot
    doctor = doctors_collection.find_one({"_id": ObjectId(doctor_id)})
    if not doctor or time_slot not in doctor["available_slots"]:
        return False
    
    # Check if slot is already booked
    existing_appointment = appointments_collection.find_one({
        "doctor_id": ObjectId(doctor_id),
        "date": appointment_date,
        "time_slot": time_slot,
        "status": {"$ne": "cancelled"}
    })
    
    return existing_appointment is None

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user_id: str = Depends(get_current_user)
):
    """Book a new appointment"""
    
    # Validate date format
    if not validate_date_format(appointment_data.date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Validate time slot format
    if not validate_time_slot_format(appointment_data.time_slot):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time slot format. Use HH:MM-HH:MM"
        )
    
    # Check if appointment date is in future
    if not is_appointment_date_future(appointment_data.date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    # Validate doctor_id format
    try:
        doctor_object_id = ObjectId(appointment_data.doctor_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid doctor ID format"
        )
    
    # Check if slot is available
    if not is_slot_available(appointment_data.doctor_id, appointment_data.date, appointment_data.time_slot):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot is not available or doctor not found"
        )
    
    # Create appointment document
    appointment_doc = {
        "user_id": ObjectId(current_user_id),
        "doctor_id": doctor_object_id,
        "date": appointment_data.date,
        "time_slot": appointment_data.time_slot,
        "status": "booked",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert appointment
    result = appointments_collection.insert_one(appointment_doc)
    
    return AppointmentResponse(
        success=True,
        message="Appointment booked successfully.",
        appointment_id=str(result.inserted_id)
    )

@router.get("/", response_model=List[dict])
async def get_user_appointments(current_user_id: str = Depends(get_current_user)):
    """Get all appointments for the current user"""
    
    # Create aggregation pipeline to join with doctors collection
    pipeline = [
        {"$match": {"user_id": ObjectId(current_user_id)}},
        {
            "$lookup": {
                "from": "doctors",
                "localField": "doctor_id",
                "foreignField": "_id",
                "as": "doctor_info"
            }
        },
        {"$unwind": "$doctor_info"},
        {
            "$project": {
                "_id": {"$toString": "$_id"},
                "doctor_name": "$doctor_info.name",
                "doctor_specialty": "$doctor_info.specialty",
                "date": 1,
                "time_slot": 1,
                "status": 1,
                "created_at": 1,
                "updated_at": 1
            }
        },
        {"$sort": {"date": 1, "time_slot": 1}}
    ]
    
    appointments = list(appointments_collection.aggregate(pipeline))
    return appointments

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    update_data: AppointmentUpdate,
    current_user_id: str = Depends(get_current_user)
):
    """Reschedule an existing appointment"""
    
    # Validate appointment_id format
    try:
        appointment_object_id = ObjectId(appointment_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid appointment ID format"
        )
    
    # Find appointment
    appointment = appointments_collection.find_one({
        "_id": appointment_object_id,
        "user_id": ObjectId(current_user_id)
    })
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check if appointment is not cancelled
    if appointment["status"] == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update cancelled appointment"
        )
    
    # Prepare update data
    update_fields = {}
    
    if update_data.date:
        if not validate_date_format(update_data.date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        if not is_appointment_date_future(update_data.date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment date must be in the future"
            )
        update_fields["date"] = update_data.date
    
    if update_data.time_slot:
        if not validate_time_slot_format(update_data.time_slot):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time slot format. Use HH:MM-HH:MM"
            )
        
        # Check if new time slot is available
        new_date = update_data.date if update_data.date else appointment["date"]
        if not is_slot_available(str(appointment["doctor_id"]), new_date, update_data.time_slot):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New time slot is not available"
            )
        update_fields["time_slot"] = update_data.time_slot
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    # Add updated_at timestamp
    update_fields["updated_at"] = datetime.utcnow()
    
    # Update appointment
    appointments_collection.update_one(
        {"_id": appointment_object_id},
        {"$set": update_fields}
    )
    
    return AppointmentResponse(
        success=True,
        message="Appointment updated successfully.",
        appointment_id=appointment_id
    )

@router.delete("/{appointment_id}", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """Cancel an appointment"""
    
    # Validate appointment_id format
    try:
        appointment_object_id = ObjectId(appointment_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid appointment ID format"
        )
    
    # Find appointment
    appointment = appointments_collection.find_one({
        "_id": appointment_object_id,
        "user_id": ObjectId(current_user_id)
    })
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check if appointment is already cancelled
    if appointment["status"] == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled"
        )
    
    # Update appointment status to cancelled
    appointments_collection.update_one(
        {"_id": appointment_object_id},
        {
            "$set": {
                "status": "cancelled",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return AppointmentResponse(
        success=True,
        message="Appointment cancelled successfully.",
        appointment_id=appointment_id
    )

# Endpoint to get available doctors (helper endpoint)
@router.get("/doctors", response_model=List[Doctor])
async def get_doctors():
    """Get list of all doctors"""
    doctors = list(doctors_collection.find())
    return [serialize_doc(doctor) for doctor in doctors]