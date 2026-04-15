# APIRouter groups related endpoints. This router handles authentication routes
# registered under "/api/v1/auth" (the prefix is set in main.py).
# Depends enables FastAPI's dependency injection for things like DB sessions.
# HTTPException returns a proper HTTP error response to the client.
# status provides readable names for HTTP status codes (e.g. HTTP_401_UNAUTHORIZED).
# Request gives us access to raw request data such as the client's IP address.
from fastapi import APIRouter, Depends, HTTPException, status, Request

# OAuth2PasswordRequestForm is a built-in FastAPI form that expects the client
# to send "username" and "password" fields (standard OAuth2 login form).
# FastAPI parses and validates these from the request body automatically.
from fastapi.security import OAuth2PasswordRequestForm

# Synchronous SQLAlchemy session (used here instead of AsyncSession because
# this route uses the standard db.query() ORM style rather than async select()).
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

# AuditLog is the model for recording security-relevant events (logins, failures, etc.)
# so administrators can review who accessed the system and when.
from app.models.audit_log import AuditLog

# verify_password checks a plain-text password against the stored bcrypt hash.
# create_access_token builds and signs a JWT that the frontend sends with every request.
from app.services.auth_service import verify_password, create_access_token

router = APIRouter()


# POST /api/v1/auth/login
# The login endpoint. The client sends a username (email) and password;
# if valid, a signed JWT access token is returned.
@router.post("/login")
def login(
    request: Request,                                        # Gives access to client IP, headers, etc.
    form_data: OAuth2PasswordRequestForm = Depends(),        # Parses the username/password form fields
    db: Session = Depends(get_db)                            # Injects an open database session
):
    # Look up the user by email address.
    # OAuth2PasswordRequestForm uses "username" as the field name by convention,
    # but we treat it as an email address in this application.
    user = db.query(User).filter(User.email == form_data.username).first()

    # If the user doesn't exist OR the password doesn't match the stored hash,
    # treat both cases identically. Giving the same error for both scenarios
    # prevents an attacker from guessing which emails are registered ("username enumeration").
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login — NFR-11, FR-42
        # Record the failed attempt in the audit log with the client's IP address
        # so administrators can spot brute-force attacks.
        log = AuditLog(
            event_type="login_failed",
            description=f"Failed login attempt for {form_data.username}",
            ip_address=request.client.host   # The IP address of whoever sent the request
        )
        db.add(log)
        db.commit()
        # 401 Unauthorized: the credentials were not accepted.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # --- Login succeeded ---

    # Update the user's last_login timestamp so we know when they were last active.
    # __import__('datetime') is an inline way to use datetime without a top-level import;
    # adding `from datetime import datetime` at the top of the file would be cleaner.
    user.last_login = __import__('datetime').datetime.utcnow()

    # Record a successful login in the audit log, linked to the user's ID.
    audit = AuditLog(
        user_id=user.id,
        event_type="login",
        description=f"User {user.email} logged in",
        ip_address=request.client.host
    )
    db.add(audit)
    db.commit()

    # Build the JWT payload:
    #   "sub" (subject) — standard JWT claim that identifies the user; stored as a string.
    #   "role" — included so other parts of the app can check permissions without
    #             an extra database query on every request.
    token = create_access_token({"sub": str(user.id), "role": user.role})

    # Return the token to the client. The frontend stores this and sends it in the
    # "Authorization: Bearer <token>" header on every subsequent API request.
    # "token_type": "bearer" is required by the OAuth2 standard.
    return {"access_token": token, "token_type": "bearer"}
