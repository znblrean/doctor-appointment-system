
# Doctor Appointment System API

A comprehensive RESTful API for managing doctor appointments with user authentication, built with FastAPI, MongoDB, and JWT authentication.

## Features

- **User Authentication**: JWT-based sign up and sign in
- **Appointment Management**: Create, read, update, and cancel appointments
- **Doctor Management**: View available doctors and their time slots
- **Data Validation**: Comprehensive input validation and error handling
- **Security**: Password hashing with bcrypt and JWT token authentication
- **Documentation**: Auto-generated API documentation with Swagger UI

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Documentation**: Swagger UI / ReDoc

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doctor-appointment-system
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Make sure MongoDB is installed and running on `mongodb://localhost:27017`

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register a new user |
| POST | `/api/v1/auth/signin` | Authenticate and get JWT token |

### Appointments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/appointments/` | Book a new appointment | Yes |
| GET | `/api/v1/appointments/` | List user's appointments | Yes |
| PUT | `/api/v1/appointments/{id}` | Update an appointment | Yes |
| DELETE | `/api/v1/appointments/{id}` | Cancel an appointment | Yes |
| GET | `/api/v1/appointments/doctors` | List available doctors | No |

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

## Request Examples

### Sign Up
```json
POST /api/v1/auth/signup
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

### Sign In
```json
POST /api/v1/auth/signin
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

### Create Appointment
```json
POST /api/v1/appointments/
Authorization: Bearer <jwt_token>
{
  "doctor_id": "doctor_object_id",
  "date": "2025-05-10",
  "time_slot": "09:00-09:30"
}
```

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "hashed_password": "bcrypt_hash",
  "created_at": "ISODate"
}
```

### Appointments Collection
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "doctor_id": "ObjectId",
  "date": "2025-05-10",
  "time_slot": "09:00-09:30",
  "status": "booked",
