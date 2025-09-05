from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.appointments import router as appointments_router
from app.database import create_sample_doctors

# Create FastAPI application
app = FastAPI(
    title="Doctor Appointment System",
    description="A comprehensive system for managing doctor appointments with user authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(appointments_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data on startup"""
    create_sample_doctors()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Doctor Appointment System API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)