from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
import json
from pydantic import BaseModel

from ..models.query import ErrorObject
from .utils import APIResponseUtils

logger = logging.getLogger(__name__)

# Create API router for authentication
router = APIRouter()

# Security scheme for protected endpoints
security = HTTPBearer()

# In-memory storage for sessions (in production, use a proper database)
user_sessions = {}
user_profiles = {}

class SignupRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class SigninRequest(BaseModel):
    email: str
    password: str

class UserProfileRequest(BaseModel):
    programmingLevel: str
    languages: list[str]
    tools: list[str]
    ram: Optional[str] = None
    processor: Optional[str] = None
    gpu: Optional[str] = None
    learningGoal: str

class UserProfileResponse(BaseModel):
    id: str
    userId: str
    programmingLevel: str
    languages: list[str]
    tools: list[str]
    ram: Optional[str] = None
    processor: Optional[str] = None
    gpu: Optional[str] = None
    learningGoal: str
    completed: bool
    createdAt: datetime
    updatedAt: datetime

class AuthResponse(BaseModel):
    token: str
    userId: str
    email: str
    name: Optional[str] = None

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

@router.post("/auth/signup", response_model=AuthResponse)
async def signup(signup_request: SignupRequest):
    """
    Register a new user account
    """
    logger.info(f"Signup attempt for email: {signup_request.email}")

    try:
        # Check if user already exists
        for session_data in user_sessions.values():
            if session_data.get("email") == signup_request.email:
                error_obj = ErrorObject(
                    error_code="USER_EXISTS",
                    message="A user with this email already exists",
                    details={"email": signup_request.email}
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=error_obj.dict()
                )

        # Create new user
        user_id = f"user_{secrets.token_hex(8)}"
        hashed_password = hash_password(signup_request.password)

        # Generate session token
        session_token = generate_session_token()

        # Store user session
        user_sessions[session_token] = {
            "userId": user_id,
            "email": signup_request.email,
            "name": signup_request.name,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow()
        }

        # Initialize empty profile
        user_profiles[user_id] = {
            "id": f"profile_{secrets.token_hex(8)}",
            "userId": user_id,
            "programmingLevel": "",
            "languages": [],
            "tools": [],
            "ram": "",
            "processor": "",
            "gpu": "",
            "learningGoal": "",
            "completed": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        logger.info(f"User created successfully: {user_id}")

        return AuthResponse(
            token=session_token,
            userId=user_id,
            email=signup_request.email,
            name=signup_request.name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}")

        error_obj = ErrorObject(
            error_code="INTERNAL_ERROR",
            message="An internal error occurred during signup",
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_obj.dict()
        )

@router.post("/auth/signin", response_model=AuthResponse)
async def signin(signin_request: SigninRequest):
    """
    Authenticate a user and return a session token
    """
    logger.info(f"Signin attempt for email: {signin_request.email}")

    try:
        # Find user by email
        user_session = None
        session_token = None
        for token, data in user_sessions.items():
            if data.get("email") == signin_request.email:
                user_session = data
                session_token = token
                break

        if not user_session:
            error_obj = ErrorObject(
                error_code="INVALID_CREDENTIALS",
                message="Invalid email or password",
                details={"email": signin_request.email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_obj.dict()
            )

        # Verify password
        if not verify_password(signin_request.password, user_session["hashed_password"]):
            error_obj = ErrorObject(
                error_code="INVALID_CREDENTIALS",
                message="Invalid email or password",
                details={"email": signin_request.email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_obj.dict()
            )

        # Generate new session token (rotate token for security)
        new_session_token = generate_session_token()
        user_sessions[new_session_token] = user_session
        # Remove old session
        if session_token:
            del user_sessions[session_token]

        logger.info(f"User signed in successfully: {user_session['userId']}")

        return AuthResponse(
            token=new_session_token,
            userId=user_session["userId"],
            email=user_session["email"],
            name=user_session.get("name")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signin: {e}")

        error_obj = ErrorObject(
            error_code="INTERNAL_ERROR",
            message="An internal error occurred during signin",
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_obj.dict()
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the current authenticated user from the session token
    """
    token = credentials.credentials

    if token not in user_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )

    return user_sessions[token]

@router.post("/profile", response_model=UserProfileResponse)
async def save_profile(
    profile_request: UserProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Save user profile data after onboarding
    """
    logger.info(f"Saving profile for user: {current_user['userId']}")

    try:
        user_id = current_user["userId"]

        if user_id not in user_profiles:
            error_obj = ErrorObject(
                error_code="USER_PROFILE_NOT_FOUND",
                message="User profile not found",
                details={"userId": user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_obj.dict()
            )

        # Update profile
        profile = user_profiles[user_id]
        profile.update({
            "programmingLevel": profile_request.programmingLevel,
            "languages": profile_request.languages,
            "tools": profile_request.tools,
            "ram": profile_request.ram,
            "processor": profile_request.processor,
            "gpu": profile_request.gpu,
            "learningGoal": profile_request.learningGoal,
            "completed": True,  # Mark as completed after onboarding
            "updatedAt": datetime.utcnow()
        })

        logger.info(f"Profile updated successfully for user: {user_id}")

        return UserProfileResponse(**profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving profile: {e}")

        error_obj = ErrorObject(
            error_code="INTERNAL_ERROR",
            message="An internal error occurred while saving profile",
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_obj.dict()
        )

@router.get("/profile/me", response_model=UserProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's profile information
    """
    logger.info(f"Fetching profile for user: {current_user['userId']}")

    try:
        user_id = current_user["userId"]

        if user_id not in user_profiles:
            error_obj = ErrorObject(
                error_code="USER_PROFILE_NOT_FOUND",
                message="User profile not found",
                details={"userId": user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_obj.dict()
            )

        profile = user_profiles[user_id]

        return UserProfileResponse(**profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching profile: {e}")

        error_obj = ErrorObject(
            error_code="INTERNAL_ERROR",
            message="An internal error occurred while fetching profile",
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_obj.dict()
        )

@router.post("/auth/signout")
async def signout(
    current_user: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Sign out the current user
    """
    logger.info(f"Signout for user: {current_user['userId']}")

    token = credentials.credentials

    # Remove session token
    if token in user_sessions:
        del user_sessions[token]

    return {"message": "Successfully signed out"}