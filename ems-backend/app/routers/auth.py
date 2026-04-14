from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.auth_service import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login — NFR-11, FR-42
        log = AuditLog(
            event_type="login_failed",
            description=f"Failed login attempt for {form_data.username}",
            ip_address=request.client.host
        )
        db.add(log)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Log successful login
    user.last_login = __import__('datetime').datetime.utcnow()
    audit = AuditLog(
        user_id=user.id,
        event_type="login",
        description=f"User {user.email} logged in",
        ip_address=request.client.host
    )
    db.add(audit)
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}