from pymongo import MongoClient
from bson import ObjectId
import os

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["doctor_appointment_db"]

# Collections
users_collection = db["users"]
doctors_collection = db["doctors"]
appointments_collection = db["appointments"]

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
        # Convert other ObjectIds to strings
        if "user_id" in doc:
            doc["user_id"] = str(doc["user_id"])
        if "doctor_id" in doc:
            doc["doctor_id"] = str(doc["doctor_id"])
    return doc

# Function to create sample doctors (run once)
def create_sample_doctors():
    sample_doctors = [
        {
            "name": "Dr. Ahmad Mohammadi",
            "specialty": "Internal Medicine",
            "available_slots": ["09:00-09:30", "09:30-10:00", "10:00-10:30", "11:00-11:30"],
            "created_at": "2025-01-01T00:00:00"
        },
        {
            "name": "Dr. Sara Hosseini",
            "specialty": "Cardiology",
            "available_slots": ["14:00-14:30", "14:30-15:00", "15:00-15:30", "16:00-16:30"],
            "created_at": "2025-01-01T00:00:00"
        },
        {
            "name": "Dr. Reza Karimi",
            "specialty": "Neurology",
            "available_slots": ["08:00-08:30", "08:30-09:00", "10:30-11:00", "11:30-12:00"],
            "created_at": "2025-01-01T00:00:00"
        }
    ]
    
    # Check if doctors already exist
    if doctors_collection.count_documents({}) == 0:
        doctors_collection.insert_many(sample_doctors)
        print("Sample doctors created successfully!")
    else:
        print("Doctors already exist in database")

# Initialize database with sample data
if __name__ == "__main__":
    create_sample_doctors()