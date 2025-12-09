"""
Main FastAPI application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.auth.routes import router as auth_router
from src.users.routes import router as users_router
from src.auth.dependencies import get_current_user
from src.auth.models import UserResponse

# Get application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Analytics Platform API",
    description="API for analytics platform with Supabase authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)
app.include_router(users_router)

# Include analysis routes
from src.analyses.routes import router as analyses_router
app.include_router(analyses_router)

# Include agents routes
from src.agents.routes import router as agents_router
app.include_router(agents_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Analytics Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


@app.get("/protected")
async def protected_route(current_user: UserResponse = Depends(get_current_user)):
    """
    Example protected route that requires authentication

    Args:
        current_user: Current authenticated user (injected by dependency)

    Returns:
        dict: Message with user data
    """
    return {
        "message": f"Hello, {current_user.email}!",
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )
