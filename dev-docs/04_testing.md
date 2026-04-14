# Phase 3: Testing
## Intelligent Energy Management System (EMS) — Beginner Developer Guide

**Project Stack:** Python/FastAPI (Backend) | React/Node.js (Frontend) | PostgreSQL (Database)  
**Document Version:** 1.0 | Date: April 2026

---

## Table of Contents
1. [Overview and Testing Strategy](#overview-and-testing-strategy)
2. [Backend Unit Tests (Python/pytest)](#backend-unit-tests)
3. [Backend Integration Tests](#backend-integration-tests)
4. [API Tests with Postman/Newman](#api-tests)
5. [Frontend Unit Tests (Vitest/React Testing Library)](#frontend-unit-tests)
6. [End-to-End Tests (Playwright)](#end-to-end-tests)
7. [Performance Tests](#performance-tests)
8. [Acceptance Criteria Verification](#acceptance-criteria-verification)
9. [Running All Tests](#running-all-tests)

---

## 1. Overview and Testing Strategy

The EMS testing strategy uses five layers aligned to the SRS Acceptance Criteria (AC-1 to AC-10):

| Layer | Tool | What it Validates |
|-------|------|-------------------|
| Unit tests | pytest (backend), Vitest (frontend) | Individual functions and components in isolation |
| Integration tests | pytest + TestClient | API endpoints and database interactions together |
| API tests | Postman / curl | Full HTTP request/response validation |
| End-to-end tests | Playwright | User workflows in a real browser |
| Performance tests | Locust | NFR-1 (5,000 msg/min), NFR-3 (3-second dashboards) |

---

## 2. Backend Unit Tests

### Step 1 — Install test dependencies

```bash
cd ems-backend
source venv/bin/activate
pip install pytest pytest-asyncio httpx pytest-cov factory-boy faker
```

---

### Step 2 — Configure pytest

```ini name=ems-backend/pytest.ini
[pytest]
testpaths = tests
asyncio_mode = auto
```

---

### Step 3 — Test database setup (use a separate test DB)

```python name=ems-backend/tests/conftest.py
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite DB for tests (fast and isolated)
TEST_DATABASE_URL = "sqlite:///./test_ems.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

---

### Step 4 — Unit tests for auth service

```python name=ems-backend/tests/unit/test_auth_service.py
# tests/unit/test_auth_service.py
"""
Tests for NFR-8 (bcrypt hashing) and token generation.
"""
import pytest
from app.services.auth_service import (
    hash_password, verify_password, create_access_token, decode_token
)

def test_password_is_hashed():
    """NFR-8: Passwords must never be stored in plain text."""
    plain = "SuperSecret123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$2b$")   # bcrypt signature

def test_correct_password_verifies():
    plain = "SuperSecret123!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True

def test_wrong_password_fails():
    hashed = hash_password("CorrectPassword")
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_encode_decode():
    data = {"sub": "42", "role": "facility_manager"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded["sub"] == "42"
    assert decoded["role"] == "facility_manager"

def test_invalid_token_returns_none():
    result = decode_token("this.is.not.a.valid.token")
    assert result is None
```

---

### Step 5 — Unit tests for telemetry validation

```python name=ems-backend/tests/unit/test_telemetry_validation.py
# tests/unit/test_telemetry_validation.py
"""
FR-9: Validate required telemetry fields.
FR-10: Reject malformed records.
FR-12: Deduplication logic.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "device_identifier": "METER-TEST-001",
    "metric_name": "active_power",
    "value": 42.5,
    "unit": "kW",
    "timestamp": "2026-04-13T08:00:00Z"
}

def test_ingest_invalid_metric_name(client):
    """FR-10: Reject records with unknown metric types."""
    bad_payload = {**VALID_PAYLOAD, "metric_name": "banana"}
    response = client.post("/api/v1/telemetry/ingest", json=bad_payload)
    assert response.status_code == 422

def test_ingest_missing_required_field(client):
    """FR-9: Records without timestamp must be rejected."""
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "timestamp"}
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 422

def test_ingest_unknown_device_returns_404(client):
    """Devices not in the registry must be rejected."""
    response = client.post("/api/v1/telemetry/ingest", json=VALID_PAYLOAD)
    assert response.status_code == 404
```

---

### Step 6 — Unit tests for alert rules

```python name=ems-backend/tests/unit/test_alert_rules.py
# tests/unit/test_alert_rules.py
"""
FR-23: Threshold-based alert generation.
FR-26: Alert severity classification.
FR-30: Duplicate suppression.
"""
import pytest
from app.services.alert_service import evaluate_threshold_rule, AlertSeverity

def test_overvoltage_triggers_critical_alert():
    """FR-23: Voltage > 260V should be CRITICAL."""
    result = evaluate_threshold_rule(
        metric="voltage", value=265.0,
        thresholds={"high_critical": 260.0, "high_warning": 250.0}
    )
    assert result is not None
    assert result.severity == AlertSeverity.critical

def test_normal_voltage_produces_no_alert():
    """No alert when value is within normal range."""
    result = evaluate_threshold_rule(
        metric="voltage", value=230.0,
        thresholds={"high_critical": 260.0, "high_warning": 250.0}
    )
    assert result is None

def test_poor_power_factor_triggers_warning():
    """FR-23: PF < 0.85 should trigger a warning."""
    result = evaluate_threshold_rule(
        metric="power_factor", value=0.75,
        thresholds={"low_critical": 0.70, "low_warning": 0.85}
    )
    assert result is not None
    assert result.severity == AlertSeverity.warning
```

---

## 3. Backend Integration Tests

```python name=ems-backend/tests/integration/test_auth_flow.py
# tests/integration/test_auth_flow.py
"""
FR-38: All protected endpoints require authentication.
FR-42: Audit logs created for login events.
"""
import pytest
from app.models.user import User, UserRole
from app.services.auth_service import hash_password

def create_test_user(db):
    user = User(
        email="manager@ems-test.co.ke",
        full_name="Test Manager",
        hashed_password=hash_password("TestPass123!"),
        role=UserRole.facility_manager,
        is_active=True
    )
    db.add(user)
    db.commit()
    return user

def test_login_with_valid_credentials(client, db):
    """FR-38: Valid credentials return a JWT token."""
    create_test_user(db)
    response = client.post("/api/v1/auth/login", data={
        "username": "manager@ems-test.co.ke",
        "password": "TestPass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_with_wrong_password_returns_401(client, db):
    create_test_user(db)
    response = client.post("/api/v1/auth/login", data={
        "username": "manager@ems-test.co.ke",
        "password": "WrongPassword"
    })
    assert response.status_code == 401

def test_protected_endpoint_without_token_returns_401(client):
    """FR-38: Unauthenticated access must be blocked."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_protected_endpoint_with_valid_token(client, db):
    create_test_user(db)
    login = client.post("/api/v1/auth/login", data={
        "username": "manager@ems-test.co.ke",
        "password": "TestPass123!"
    })
    token = login.json()["access_token"]
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

---

```python name=ems-backend/tests/integration/test_telemetry_pipeline.py
# tests/integration/test_telemetry_pipeline.py
"""
AC-1: Successful ingestion without errors.
AC-2: Telemetry available for display (stored in DB).
FR-14, FR-15: Device status updated after ingestion.
"""
import pytest
from app.models.building import Building
from app.models.device import Device

def create_test_device(db):
    building = Building(name="Test Building", address="Nairobi", timezone="Africa/Nairobi")
    db.add(building)
    db.flush()
    device = Device(
        device_identifier="METER-INTEG-001",
        device_type="smart_meter",
        protocol="http",
        building_id=building.id,
        heartbeat_interval_seconds=60
    )
    db.add(device)
    db.commit()
    return device

def test_telemetry_ingest_and_retrieval(client, db):
    create_test_device(db)
    payload = {
        "device_identifier": "METER-INTEG-001",
        "metric_name": "voltage",
        "value": 231.5,
        "unit": "V",
        "timestamp": "2026-04-13T09:00:00Z"
    }
    post_response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert post_response.status_code == 202

    get_response = client.get("/api/v1/telemetry/METER-INTEG-001?metric=voltage")
    assert get_response.status_code == 200
    records = get_response.json()
    assert len(records) == 1
    assert records[0]["value"] == 231.5

def test_duplicate_telemetry_is_rejected(client, db):
    """FR-12: Duplicate records must not be stored twice."""
    create_test_device(db)
    payload = {
        "device_identifier": "METER-INTEG-001",
        "metric_name": "active_power",
        "value": 50.0,
        "unit": "kW",
        "timestamp": "2026-04-13T10:00:00Z"
    }
    r1 = client.post("/api/v1/telemetry/ingest", json=payload)
    r2 = client.post("/api/v1/telemetry/ingest", json=payload)
    assert r1.status_code == 202
    assert r2.json()["status"] == "duplicate"

    records = client.get("/api/v1/telemetry/METER-INTEG-001?metric=active_power").json()
    assert len(records) == 1   # Only one stored
```

---

## 4. API Tests with Postman

### Step 1 — Install Newman (Postman CLI runner)

```bash
npm install -g newman
```

### Step 2 — Create a Postman collection file

```json name=ems-backend/tests/api/ems_api_tests.postman_collection.json
{
  "info": { "name": "EMS API Tests", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "item": [
    {
      "name": "Health Check",
      "request": { "method": "GET", "url": "{{BASE_URL}}/health" },
      "event": [{ "listen": "test", "script": { "exec": [
        "pm.test('Status 200', () => pm.response.to.have.status(200));",
        "pm.test('Status is ok', () => pm.expect(pm.response.json().status).to.eql('ok'));"
      ]}}]
    },
    {
      "name": "Login - Valid",
      "request": {
        "method": "POST",
        "url": "{{BASE_URL}}/api/v1/auth/login",
        "body": { "mode": "urlencoded", "urlencoded": [
          {"key": "username", "value": "admin@ems.co.ke"},
          {"key": "password", "value": "AdminPass123!"}
        ]}
      },
      "event": [{ "listen": "test", "script": { "exec": [
        "pm.test('Returns 200', () => pm.response.to.have.status(200));",
        "pm.test('Has access_token', () => pm.expect(pm.response.json()).to.have.property('access_token'));",
        "pm.environment.set('TOKEN', pm.response.json().access_token);"
      ]}}]
    },
    {
      "name": "Ingest Telemetry",
      "request": {
        "method": "POST",
        "url": "{{BASE_URL}}/api/v1/telemetry/ingest",
        "header": [{"key": "Authorization", "value": "Bearer {{TOKEN}}"}],
        "body": { "mode": "raw", "raw": "{\"device_identifier\":\"METER-001\",\"metric_name\":\"voltage\",\"value\":230.1,\"unit\":\"V\",\"timestamp\":\"2026-04-13T12:00:00Z\"}" }
      },
      "event": [{ "listen": "test", "script": { "exec": [
        "pm.test('Returns 202', () => pm.response.to.have.status(202));"
      ]}}]
    }
  ]
}
```

### Step 3 — Run the collection

```bash
newman run tests/api/ems_api_tests.postman_collection.json \
  --env-var "BASE_URL=http://localhost:8000" \
  --reporters cli,json \
  --reporter-json-export tests/api/results.json
```

---

## 5. Frontend Unit Tests

### Step 1 — Install test dependencies

```bash
cd ems-frontend
npm install --save-dev vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event msw
```

### Step 2 — Configure Vitest

```javascript name=ems-frontend/vite.config.js
// vite.config.js — updated with test config
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js'
  }
})
```

```javascript name=ems-frontend/src/test/setup.js
// src/test/setup.js
import '@testing-library/jest-dom'
```

### Step 3 — Component test example

```javascript name=ems-frontend/src/components/__tests__/AlertBadge.test.jsx
// src/components/__tests__/AlertBadge.test.jsx
/**
 * FR-26, FR-22: Alerts display correct severity labels and colors.
 */
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import AlertBadge from '../AlertBadge'

describe('AlertBadge', () => {
  it('renders CRITICAL with red styling', () => {
    render(<AlertBadge severity="critical" />)
    const badge = screen.getByText(/critical/i)
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-red-100')
  })

  it('renders WARNING with yellow styling', () => {
    render(<AlertBadge severity="warning" />)
    expect(screen.getByText(/warning/i)).toHaveClass('bg-yellow-100')
  })

  it('renders INFORMATIONAL with blue styling', () => {
    render(<AlertBadge severity="informational" />)
    expect(screen.getByText(/informational/i)).toHaveClass('bg-blue-100')
  })
})
```

### Step 4 — Run frontend tests

```bash
npm run test
# Or with coverage:
npm run test -- --coverage
```

---

## 6. End-to-End Tests (Playwright)

### Step 1 — Install Playwright

```bash
cd ems-frontend
npm install --save-dev @playwright/test
npx playwright install chromium
```

### Step 2 — Write E2E tests

```javascript name=ems-frontend/tests/e2e/login.spec.js
// tests/e2e/login.spec.js
/**
 * AC-4: Users can log in and access only permitted features.
 */
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('facility manager can log in and view dashboard', async ({ page }) => {
    await page.goto('http://localhost:5173/login')

    await page.fill('[data-testid="email-input"]', 'manager@ems.co.ke')
    await page.fill('[data-testid="password-input"]', 'TestPass123!')
    await page.click('[data-testid="login-button"]')

    await expect(page).toHaveURL(/dashboard/)
    await expect(page.locator('[data-testid="kpi-total-energy"]')).toBeVisible()
  })

  test('wrong password shows error message', async ({ page }) => {
    await page.goto('http://localhost:5173/login')
    await page.fill('[data-testid="email-input"]', 'manager@ems.co.ke')
    await page.fill('[data-testid="password-input"]', 'WrongPassword')
    await page.click('[data-testid="login-button"]')
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials')
  })
})
```

```javascript name=ems-frontend/tests/e2e/alerts.spec.js
// tests/e2e/alerts.spec.js
/**
 * AC-3: Alerts display correct severity and can be acknowledged.
 */
import { test, expect } from '@playwright/test'

test('facility manager can acknowledge an alert', async ({ page }) => {
  // Login
  await page.goto('http://localhost:5173/login')
  await page.fill('[data-testid="email-input"]', 'manager@ems.co.ke')
  await page.fill('[data-testid="password-input"]', 'TestPass123!')
  await page.click('[data-testid="login-button"]')

  // Navigate to alerts
  await page.click('[data-testid="nav-alerts"]')
  await expect(page.locator('[data-testid="alerts-page-title"]')).toBeVisible()

  // Acknowledge first alert
  const firstAck = page.locator('[data-testid="acknowledge-btn"]').first()
  await firstAck.click()
  await expect(page.locator('[data-testid="alert-status"]').first()).toContainText('acknowledged')
})
```

### Step 3 — Run E2E tests

```bash
npx playwright test
# View HTML report:
npx playwright show-report
```

---

## 7. Performance Tests

### Step 1 — Install Locust

```bash
cd ems-backend
pip install locust
```

### Step 2 — Create load test script

```python name=ems-backend/tests/performance/locustfile.py
# tests/performance/locustfile.py
"""
NFR-1: System shall ingest at least 5,000 telemetry messages/minute.
NFR-3: Dashboard renders within 3 seconds for 95% of requests.
"""
from locust import HttpUser, task, between
from datetime import datetime, timezone, timedelta
import random
import json

class EMSUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Log in and store token."""
        response = self.client.post("/api/v1/auth/login", data={
            "username": "loadtest@ems.co.ke",
            "password": "LoadTest123!"
        })
        self.token = response.json().get("access_token", "")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def ingest_telemetry(self):
        """NFR-1: High-frequency ingestion task."""
        metrics = ["voltage", "current", "active_power", "power_factor"]
        payload = {
            "device_identifier": f"METER-LOAD-{random.randint(1, 50):03d}",
            "metric_name": random.choice(metrics),
            "value": round(random.uniform(10, 300), 2),
            "unit": "kW",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.client.post("/api/v1/telemetry/ingest", json=payload, headers=self.headers)

    @task(2)
    def view_dashboard(self):
        """NFR-3: Dashboard must load within 3 seconds."""
        self.client.get("/api/v1/buildings/1/dashboard", headers=self.headers)

    @task(1)
    def view_alerts(self):
        self.client.get("/api/v1/alerts/?building_id=1", headers=self.headers)
```

### Step 3 — Run Locust

```bash
locust -f tests/performance/locustfile.py \
  --host http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 2m \
  --headless \
  --csv tests/performance/results
```

**Target:** At 100 concurrent users, ingestion median response time should be under 200ms and the 95th percentile dashboard response should be under 3,000ms (NFR-3).

---

## 8. Acceptance Criteria Verification

| AC | Test File | Pass Condition |
|----|-----------|---------------|
| AC-1 | `test_telemetry_pipeline.py` | 24-hour ingestion test returns no 5xx errors |
| AC-2 | `test_telemetry_pipeline.py` | 95% of records appear in DB within 10 seconds |
| AC-3 | `test_alert_rules.py`, `alerts.spec.js` | 100% of threshold breach test cases generate correct alerts |
| AC-4 | `test_auth_flow.py`, `login.spec.js` | 100% RBAC test cases pass |
| AC-5 | `test_reports.py` | Monthly report generated in < 60 seconds |
| AC-6 | `test_auth_flow.py` | Audit records retrievable for all auth and config events |
| AC-7 | `test_control_actions.py` | Locked-out assets block 100% of control commands |
| AC-8 | `test_telemetry_pipeline.py::test_duplicate_telemetry_is_rejected` | No duplicate records after reconnect |
| AC-9 | `test_multibuilding.py` | Three test sites load with site-specific settings |
| AC-10 | Manual stakeholder walkthrough | Stakeholder sign-off |

---

### Run all backend tests with coverage

```bash
cd ems-backend
pytest --cov=app --cov-report=html --cov-report=term-missing
# Open htmlcov/index.html for the full coverage report
```

---

*Next: [04_security.md](04_security.md)*