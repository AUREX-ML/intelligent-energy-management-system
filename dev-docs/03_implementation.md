# Phase 2: Implementation
## Intelligent Energy Management System (EMS) — Beginner Developer Guide

**Project Stack:** Python/FastAPI (Backend) | React/Node.js (Frontend) | PostgreSQL (Database)  
**Document Version:** 1.0 | Date: April 2026

---

## Table of Contents
1. [Overview](#overview)
2. [Database Schema and Migrations](#database-schema-and-migrations)
3. [Backend Implementation](#backend-implementation)
4. [API Endpoints Reference](#api-endpoints-reference)
5. [Frontend Implementation](#frontend-implementation)
6. [MQTT Telemetry Ingestion](#mqtt-telemetry-ingestion)
7. [Background Tasks](#background-tasks)
8. [Running the Application Locally](#running-the-application-locally)

---

## 1. Overview

This phase covers writing the actual code for the EMS. It maps directly to the SRS requirements (FR-1 through FR-60). The sections are ordered in the natural build sequence:

1. Database tables first (the foundation).
2. Backend API (the brain).
3. Frontend UI (the face).
4. Telemetry ingestion (the ears).
5. Background tasks (the nervous system).

---

## 2. Database Schema and Migrations

### Step 1 — Initialize Alembic (database migration tool)

```bash
cd ems-backend
source venv/bin/activate
alembic init alembic
```

Edit `alembic/env.py` — replace the `target_metadata` section:

```python
# alembic/env.py  (relevant lines)
from app.database import Base
from app import models  # ensure all models are imported

target_metadata = Base.metadata
```

Edit `alembic.ini` — update the database URL line:
```ini
sqlalchemy.url = postgresql://ems_user:StrongPassword123!@localhost:5432/ems_db
```

---

### Step 2 — Create the database module

```python name=ems-backend/app/database.py
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dependency to inject DB session into route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### Step 3 — Create the settings module

```python name=ems-backend/app/config.py
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### Step 4 — Define the ORM models

```python name=ems-backend/app/models/__init__.py
# app/models/__init__.py
from .user import User
from .building import Building
from .device import Device
from .telemetry import TelemetryRecord
from .alert import Alert
from .audit_log import AuditLog
from .control_action import ControlAction
```

```python name=ems-backend/app/models/user.py
# app/models/user.py
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.database import Base

class UserRole(str, enum.Enum):
    system_admin = "system_admin"
    facility_manager = "facility_manager"
    technician = "technician"
    executive_viewer = "executive_viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
```

```python name=ems-backend/app/models/device.py
# app/models/device.py
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float
from app.database import Base

class DeviceStatus(str, enum.Enum):
    online = "online"
    degraded = "degraded"
    offline = "offline"
    unknown = "unknown"

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_identifier = Column(String, unique=True, nullable=False, index=True)
    device_type = Column(String, nullable=False)          # smart_meter, submeter, sensor
    protocol = Column(String, nullable=False)             # mqtt, http
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    location_description = Column(String)
    heartbeat_interval_seconds = Column(Integer, default=60)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.unknown)
    last_seen_at = Column(DateTime, nullable=True)
    commissioned_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_controllable = Column(Boolean, default=False)
    is_safety_critical = Column(Boolean, default=False)
```

```python name=ems-backend/app/models/telemetry.py
# app/models/telemetry.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from app.database import Base

class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False)    # voltage, current, active_power, etc.
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    source_timestamp = Column(DateTime, nullable=False)   # Original device timestamp (UTC)
    received_at = Column(DateTime, default=datetime.utcnow)
    is_valid = Column(Boolean, default=True)
    quality_flag = Column(String, default="good")         # good, missing, duplicate, invalid
```

```python name=ems-backend/app/models/alert.py
# app/models/alert.py
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from app.database import Base

class AlertSeverity(str, enum.Enum):
    informational = "informational"
    warning = "warning"
    high = "high"
    critical = "critical"

class AlertStatus(str, enum.Enum):
    open = "open"
    acknowledged = "acknowledged"
    assigned = "assigned"
    resolved = "resolved"
    closed = "closed"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    metric_name = Column(String)
    triggered_value = Column(String)
    threshold_condition = Column(String)
    severity = Column(Enum(AlertSeverity), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.open)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
```

```python name=ems-backend/app/models/audit_log.py
# app/models/audit_log.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String, nullable=False)   # login, logout, config_change, control_action
    description = Column(Text, nullable=False)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

### Step 5 — Generate and run the first migration

```bash
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

Verify in psql:
```sql
\c ems_db
\dt
-- You should see: users, devices, telemetry_records, alerts, audit_logs, buildings, etc.
```

---

## 3. Backend Implementation

### Step 1 — Create the FastAPI application entry point

```python name=ems-backend/app/main.py
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, devices, telemetry, alerts, reports, users, buildings

app = FastAPI(
    title="EMS API",
    description="Intelligent Energy Management System API",
    version="1.0.0"
)

# Allow requests from the frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(buildings.router, prefix="/api/v1/buildings", tags=["Buildings"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["Telemetry"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "EMS API"}
```

---

### Step 2 — Authentication service (FR-38, FR-39, NFR-8)

```python name=ems-backend/app/services/auth_service.py
# app/services/auth_service.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """Store passwords only as bcrypt hashes — NFR-8."""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
```

---

### Step 3 — Authentication router

```python name=ems-backend/app/routers/auth.py
# app/routers/auth.py
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
```

---

### Step 4 — Telemetry ingestion router (FR-8 to FR-15)

```python name=ems-backend/app/routers/telemetry.py
# app/routers/telemetry.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models.device import Device
from app.models.telemetry import TelemetryRecord

router = APIRouter()

class TelemetryPayload(BaseModel):
    device_identifier: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime              # Source device timestamp (UTC)
    message_id: Optional[str] = None

VALID_METRICS = {
    "voltage", "current", "active_power", "reactive_power",
    "apparent_power", "power_factor", "frequency",
    "cumulative_energy", "demand"
}

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_telemetry(payload: TelemetryPayload, db: Session = Depends(get_db)):
    """
    FR-8: Ingest telemetry via HTTP.
    FR-9: Validate required fields.
    FR-10: Reject/quarantine malformed records.
    FR-12: Deduplicate using device_id + metric + timestamp.
    """
    # FR-9 Validate metric type
    if payload.metric_name not in VALID_METRICS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid metric_name '{payload.metric_name}'"
        )

    # Lookup device by identifier
    device = db.query(Device).filter(
        Device.device_identifier == payload.device_identifier,
        Device.is_active == True
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # FR-12: Deduplication check
    existing = db.query(TelemetryRecord).filter(
        TelemetryRecord.device_id == device.id,
        TelemetryRecord.metric_name == payload.metric_name,
        TelemetryRecord.source_timestamp == payload.timestamp
    ).first()
    if existing:
        return {"status": "duplicate", "message": "Record already exists"}

    record = TelemetryRecord(
        device_id=device.id,
        metric_name=payload.metric_name,
        value=payload.value,
        unit=payload.unit,
        source_timestamp=payload.timestamp,
        is_valid=True,
        quality_flag="good"
    )
    db.add(record)

    # Update device last seen — FR-14, FR-15
    device.last_seen_at = datetime.utcnow()
    device.status = "online"
    db.commit()

    return {"status": "accepted"}

@router.get("/{device_identifier}")
def get_device_telemetry(
    device_identifier: str,
    metric: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Return recent telemetry for a device — FR-1, FR-6."""
    device = db.query(Device).filter(
        Device.device_identifier == device_identifier
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    query = db.query(TelemetryRecord).filter(TelemetryRecord.device_id == device.id)
    if metric:
        query = query.filter(TelemetryRecord.metric_name == metric)

    records = query.order_by(TelemetryRecord.source_timestamp.desc()).limit(limit).all()
    return records
```

---

### Step 5 — Alerts router (FR-23 to FR-30)

```python name=ems-backend/app/routers/alerts.py
# app/routers/alerts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.alert import Alert, AlertStatus

router = APIRouter()

@router.get("/")
def list_alerts(building_id: int = None, status: str = None, db: Session = Depends(get_db)):
    """FR-28: Return alerts filtered by building and/or status."""
    query = db.query(Alert)
    if building_id:
        query = query.filter(Alert.building_id == building_id)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.created_at.desc()).limit(200).all()

@router.patch("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """FR-28: Acknowledge an open alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.acknowledged
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    return {"status": "acknowledged", "alert_id": alert_id}

@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: int, notes: str = "", db: Session = Depends(get_db)):
    """FR-28, FR-29: Resolve alert with notes."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.resolved
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = notes
    db.commit()
    return {"status": "resolved", "alert_id": alert_id}
```

---

## 4. API Endpoints Reference

| Method | Endpoint | Description | SRS Ref |
|--------|----------|-------------|---------|
| POST | `/api/v1/auth/login` | User login, returns JWT | FR-38 |
| GET | `/api/v1/users/me` | Current user profile | FR-39 |
| GET | `/api/v1/buildings/` | List all buildings | FR-57, FR-58 |
| GET | `/api/v1/buildings/{id}/dashboard` | Site dashboard KPIs | FR-17, FR-7 |
| POST | `/api/v1/devices/` | Register a device | FR-52 |
| GET | `/api/v1/devices/` | List all devices | FR-14 |
| POST | `/api/v1/telemetry/ingest` | Ingest telemetry | FR-8 |
| GET | `/api/v1/telemetry/{device_id}` | Query device telemetry | FR-1 |
| GET | `/api/v1/alerts/` | List alerts | FR-28 |
| PATCH | `/api/v1/alerts/{id}/acknowledge` | Acknowledge alert | FR-28 |
| GET | `/api/v1/reports/monthly` | Generate monthly report | FR-31 |
| POST | `/api/v1/control/{device_id}/command` | Send control command | FR-44 |

---

## 5. Frontend Implementation

### Step 1 — Set up the Vite + React app

```javascript name=ems-frontend/vite.config.js
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

---

### Step 2 — API client with Axios

```javascript name=ems-frontend/src/api/client.js
// src/api/client.js
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

// Attach JWT token to every request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('ems_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 Unauthorized — redirect to login
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ems_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

---

### Step 3 — Auth store (Zustand)

```javascript name=ems-frontend/src/store/authStore.js
// src/store/authStore.js
import { create } from 'zustand'
import apiClient from '../api/client'

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('ems_token'),
  isAuthenticated: !!localStorage.getItem('ems_token'),

  login: async (email, password) => {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    const response = await apiClient.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    const { access_token } = response.data
    localStorage.setItem('ems_token', access_token)
    set({ token: access_token, isAuthenticated: true })
    return response.data
  },

  logout: () => {
    localStorage.removeItem('ems_token')
    set({ user: null, token: null, isAuthenticated: false })
  }
}))

export default useAuthStore
```

---

### Step 4 — Dashboard page component (FR-16, FR-17, FR-22)

```javascript name=ems-frontend/src/pages/DashboardPage.jsx
// src/pages/DashboardPage.jsx
import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import apiClient from '../api/client'

export default function DashboardPage({ buildingId }) {
  const [kpis, setKpis] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [trend, setTrend] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [kpiRes, alertRes] = await Promise.all([
          apiClient.get(`/buildings/${buildingId}/dashboard`),
          apiClient.get(`/alerts/?building_id=${buildingId}&status=open`)
        ])
        setKpis(kpiRes.data.kpis)
        setAlerts(alertRes.data)
        setTrend(kpiRes.data.trend)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    // FR-2: Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [buildingId])

  if (loading) return <div className="p-6">Loading dashboard...</div>

  return (
    <div className="p-6 space-y-6">
      {/* KPI Cards — FR-7 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="Total Energy (kWh)" value={kpis?.total_energy_kwh} />
        <KpiCard label="Peak Demand (kW)" value={kpis?.peak_demand_kw} />
        <KpiCard label="Avg Power Factor" value={kpis?.avg_power_factor} />
        <KpiCard label="Est. Cost (KES)" value={kpis?.estimated_cost_kes} />
      </div>

      {/* Trend chart — FR-18 */}
      <div className="bg-white rounded-xl shadow p-4">
        <h2 className="text-lg font-semibold mb-4">Active Power Trend (kW)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#2563eb" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Active alerts — FR-26, FR-22 */}
      <div className="bg-white rounded-xl shadow p-4">
        <h2 className="text-lg font-semibold mb-4">Active Alerts</h2>
        {alerts.length === 0 ? (
          <p className="text-green-600">No active alerts</p>
        ) : (
          <ul className="space-y-2">
            {alerts.map(alert => (
              <li key={alert.id} className={`p-3 rounded-lg border ${
                alert.severity === 'critical' ? 'border-red-500 bg-red-50' :
                alert.severity === 'high' ? 'border-orange-400 bg-orange-50' :
                'border-yellow-300 bg-yellow-50'
              }`}>
                <strong>{alert.severity.toUpperCase()}</strong> — {alert.metric_name} |{' '}
                {alert.triggered_value} | {new Date(alert.created_at).toLocaleString()}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function KpiCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl shadow p-4 text-center">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-blue-700">{value ?? '—'}</p>
    </div>
  )
}
```

---

## 6. MQTT Telemetry Ingestion

### Step 1 — Install a local MQTT broker (Mosquitto)

**Ubuntu:**
```bash
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl start mosquitto
```

**macOS:**
```bash
brew install mosquitto
brew services start mosquitto
```

---

### Step 2 — MQTT subscriber service

```python name=ems-backend/app/services/mqtt_subscriber.py
# app/services/mqtt_subscriber.py
"""
FR-8: Ingest telemetry via MQTT.
Run this as a separate process: python -m app.services.mqtt_subscriber
"""
import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from app.config import settings
from app.database import SessionLocal
from app.models.device import Device
from app.models.telemetry import TelemetryRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mqtt_subscriber")

TOPIC = "ems/+/telemetry"   # Wildcard: ems/{device_identifier}/telemetry

def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected to MQTT broker (rc={rc})")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    db = SessionLocal()
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        device_identifier = msg.topic.split("/")[1]

        # FR-9: Validate required fields
        required = ["metric_name", "value", "unit", "timestamp"]
        if not all(k in payload for k in required):
            logger.warning(f"Malformed payload from {device_identifier}: {payload}")
            return

        device = db.query(Device).filter(
            Device.device_identifier == device_identifier,
            Device.is_active == True
        ).first()
        if not device:
            logger.warning(f"Unknown device: {device_identifier}")
            return

        source_ts = datetime.fromisoformat(payload["timestamp"])

        # FR-12: Deduplication
        exists = db.query(TelemetryRecord).filter(
            TelemetryRecord.device_id == device.id,
            TelemetryRecord.metric_name == payload["metric_name"],
            TelemetryRecord.source_timestamp == source_ts
        ).first()
        if exists:
            return

        record = TelemetryRecord(
            device_id=device.id,
            metric_name=payload["metric_name"],
            value=float(payload["value"]),
            unit=payload["unit"],
            source_timestamp=source_ts,
            is_valid=True,
            quality_flag="good"
        )
        db.add(record)
        device.last_seen_at = datetime.utcnow()
        device.status = "online"
        db.commit()
        logger.info(f"Stored: {device_identifier} | {payload['metric_name']} = {payload['value']}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
    client.loop_forever()
```

---

## 7. Background Tasks

```python name=ems-backend/app/tasks/heartbeat_monitor.py
# app/tasks/heartbeat_monitor.py
"""
FR-15: Detect devices that have missed their heartbeat and create alerts.
Run with Celery beat scheduler.
"""
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.device import Device, DeviceStatus
from app.models.alert import Alert, AlertSeverity, AlertStatus

def check_device_heartbeats():
    db = SessionLocal()
    try:
        devices = db.query(Device).filter(Device.is_active == True).all()
        now = datetime.utcnow()

        for device in devices:
            if not device.last_seen_at:
                continue
            threshold = timedelta(seconds=device.heartbeat_interval_seconds * 3)
            if now - device.last_seen_at > threshold:
                # Mark device as offline
                device.status = DeviceStatus.offline

                # Check if an open comm-fault alert already exists (FR-30: suppress duplicates)
                existing_alert = db.query(Alert).filter(
                    Alert.device_id == device.id,
                    Alert.status == AlertStatus.open,
                    Alert.metric_name == "communication"
                ).first()
                if not existing_alert:
                    alert = Alert(
                        device_id=device.id,
                        building_id=device.building_id,
                        metric_name="communication",
                        triggered_value="no heartbeat",
                        threshold_condition=f"no message for >{device.heartbeat_interval_seconds * 3}s",
                        severity=AlertSeverity.high,
                        status=AlertStatus.open
                    )
                    db.add(alert)

        db.commit()
    finally:
        db.close()
```

---

## 8. Running the Application Locally

### Terminal 1 — Start the backend

```bash
cd ems-backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

Visit **http://localhost:8000/docs** for the interactive Swagger API documentation.

---

### Terminal 2 — Start the MQTT subscriber

```bash
cd ems-backend
source venv/bin/activate
python -m app.services.mqtt_subscriber
```

---

### Terminal 3 — Start the frontend

```bash
cd ems-frontend
npm run dev
```

Visit **http://localhost:5173** for the EMS dashboard.

---

### Quick test — send a sample telemetry message

```bash
curl -X POST http://localhost:8000/api/v1/telemetry/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "device_identifier": "METER-001",
    "metric_name": "active_power",
    "value": 42.5,
    "unit": "kW",
    "timestamp": "2026-04-13T08:00:00Z"
  }'
```

Expected response: `{"status": "accepted"}`

---

*Next: [03_testing.md](03_testing.md)*