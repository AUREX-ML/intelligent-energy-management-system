# Phase 1: Environment Setup
## Intelligent Energy Management System (EMS) — Beginner Developer Guide

**Project Stack:** Python (Backend) | Node.js (Frontend) | PostgreSQL (Database)  
**Document Version:** 1.0 | Date: April 2026

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [System Requirements](#system-requirements)
4. [Installing Core Tools](#installing-core-tools)
5. [Setting Up PostgreSQL](#setting-up-postgresql)
6. [Setting Up the Python Backend](#setting-up-the-python-backend)
7. [Setting Up the Node.js Frontend](#setting-up-the-nodejs-frontend)
8. [Environment Variables](#environment-variables)
9. [Project Folder Structure](#project-folder-structure)
10. [Verifying Your Setup](#verifying-your-setup)

---

## 1. Overview

This guide walks a beginner developer through setting up a complete local development environment for the EMS platform. By the end of this phase you will have:

- PostgreSQL running locally with an EMS database created.
- A Python virtual environment with all backend dependencies installed.
- A Node.js project initialized with all frontend dependencies installed.
- Environment variable files configured.
- A verified, working project structure.

---

## 2. Prerequisites

No prior DevOps experience is required, but you should:

- Know how to open a terminal (Command Prompt / PowerShell on Windows, Terminal on macOS/Linux).
- Have administrator/sudo access on your machine.
- Have a code editor installed — **VS Code is recommended** (https://code.visualstudio.com).

---

## 3. System Requirements

| Component | Minimum |
|-----------|---------|
| OS | Windows 10, macOS 12+, or Ubuntu 20.04+ |
| RAM | 8 GB |
| Disk Space | 10 GB free |
| Internet | Required for initial setup |

---

## 4. Installing Core Tools

### Step 1 — Install Git

Git is used for version control.

**Windows:**
Download from https://git-scm.com/download/win and run the installer.

**macOS:**
```bash
xcode-select --install
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install git -y
```

Verify:
```bash
git --version
# Expected output: git version 2.x.x
```

---

### Step 2 — Install Python 3.12+

**Windows / macOS:**
Download from https://www.python.org/downloads/ — check **"Add Python to PATH"** during install.

**Ubuntu/Debian:**
```bash
sudo apt install python3.12 python3.12-venv python3-pip -y
```

Verify:
```bash
python3 --version
# Expected output: Python 3.12.x
```

---

### Step 3 — Install Node.js 24 LTS

**All platforms — recommended via Node Version Manager (nvm):**

**macOS / Linux:**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc    # or ~/.zshrc on macOS
nvm install 24
nvm use 24
```

**Windows:**
Download nvm-windows from https://github.com/coreybutler/nvm-windows/releases  
Then in PowerShell (as Admin):
```powershell
nvm install 24
nvm use 24
```

Verify:
```bash
node --version   # Expected: v24.x.x
npm --version    # Expected: 11.x.x
```

---

### Step 4 — Install PostgreSQL 16+

**Windows:**
Download from https://www.postgresql.org/download/windows/ — use the interactive installer. Remember the **superuser password** you set for the `postgres` user.

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

Verify:
```bash
psql --version
# Expected: psql (PostgreSQL) 16.x
```

---

### Step 5 — Install pgAdmin (Optional GUI)

Download from https://www.pgadmin.org/download/ — useful for visualizing your database tables.

---

## 5. Setting Up PostgreSQL

### Step 1 — Access the PostgreSQL prompt

**macOS / Linux:**
```bash
sudo -u postgres psql
```

**Windows (in Command Prompt):**
```cmd
psql -U postgres
```

Enter the password you set during installation.

---

### Step 2 — Create the EMS database and user

Run these commands inside the `psql` prompt:

```sql
-- Create a dedicated database user
CREATE USER ems_user WITH PASSWORD 'StrongPassword123!';

-- Create the EMS database
CREATE DATABASE ems_db OWNER ems_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE ems_db TO ems_user;

-- Exit
\q
```

---

### Step 3 — Verify the connection

```bash
psql -U ems_user -d ems_db -h localhost
# You should see: ems_db=>
\q
```

---

## 6. Setting Up the Python Backend

### Step 1 — Clone the repository (or create the folder)

```bash
git clone https://github.com/your-org/ems-backend.git
cd ems-backend

# Or if starting fresh:
mkdir ems-backend && cd ems-backend
git init
```

---

### Step 2 — Create and activate a virtual environment

```bash
python3 -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Activate on Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Activate on Windows (CMD):
venv\Scripts\activate.bat
```

Your terminal prompt should now show `(venv)`.

---

### Step 3 — Create requirements.txt

Create a file named `requirements.txt` in the `ems-backend` folder:

```text
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.7.1
pydantic-settings==2.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.6
paho-mqtt==2.0.0
celery==5.4.0
redis==5.0.4
```

---

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 5 — Verify FastAPI installation

```bash
python -c "import fastapi; print(fastapi.__version__)"
# Expected: 0.111.0
```

---

## 7. Setting Up the Node.js Frontend

### Step 1 — Navigate to the frontend folder

```bash
cd ..
mkdir ems-frontend && cd ems-frontend
npm init -y
```

---

### Step 2 — Install dependencies

```bash
# Core framework
npm install react@18 react-dom@18

# Build tooling
npm install --save-dev vite@8 @vitejs/plugin-react

# UI and charting
npm install recharts@2 chart.js@4 react-chartjs-2@5

# HTTP client and state management
npm install axios@1 zustand@4

# Routing
npm install react-router-dom@6

# Styling
npm install tailwindcss@3 postcss autoprefixer

# Date handling
npm install date-fns@3

# Table component
npm install @tanstack/react-table@8

# Notifications / Toasts
npm install react-hot-toast@2

# Form handling
npm install react-hook-form@7 zod@3 @hookform/resolvers@3

# PDF and CSV export
npm install jspdf@2 jspdf-autotable@3 papaparse@5
```

---

### Step 3 — Initialize Tailwind CSS

```bash
npx tailwindcss init -p
```

---

### Step 4 — Verify Node setup

```bash
node -e "console.log('Node.js is working')"
# Expected: Node.js is working
```

---

## 8. Environment Variables

### Backend — create `ems-backend/.env`

```env
# Application
APP_NAME=EMS-Backend
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://ems_user:StrongPassword123!@localhost:5432/ems_db

# Security
SECRET_KEY=your-very-long-random-secret-key-replace-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT Broker
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Redis (for Celery task queue)
REDIS_URL=redis://localhost:6379/0

# Email notifications (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

> ⚠️ **NEVER commit `.env` to version control.** Add `.env` to your `.gitignore` file.

---

### Frontend — create `ems-frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=EMS Dashboard
VITE_ENV=development
```

---

### Create `.gitignore` in both projects

**Backend** `ems-backend/.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
*.egg-info/
.pytest_cache/
```

**Frontend** `ems-frontend/.gitignore`:
```
node_modules/
dist/
.env
.env.local
```

---

## 9. Project Folder Structure

```
ems-project/
├── ems-backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings loaded from .env
│   │   ├── database.py          # SQLAlchemy engine and session
│   │   ├── models/              # ORM models (User, Device, Telemetry, Alert...)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routers/             # API route handlers
│   │   ├── services/            # Business logic layer
│   │   ├── tasks/               # Celery background tasks
│   │   └── utils/               # Helper functions
│   ├── alembic/                 # Database migration files
│   ├── tests/                   # Backend tests
│   ├── requirements.txt
│   └── .env
│
├── ems-frontend/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # Root component + router
│   │   ├── api/                 # Axios API clients
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page-level components
│   │   ├── store/               # Zustand state stores
│   │   ├── hooks/               # Custom React hooks
│   │   └── utils/               # Helper functions
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env
│
└── README.md
```

---

## 10. Verifying Your Setup

Run each check. All should return the expected output.

```bash
# 1. Python version
python3 --version
# Expected: Python 3.12.x

# 2. Virtual environment active (you should see (venv))
which python   # macOS/Linux
where python   # Windows

# 3. Node.js
node --version
# Expected: v24.x.x

# 4. PostgreSQL connection
psql -U ems_user -d ems_db -h localhost -c "SELECT version();"
# Expected: PostgreSQL 16.x...

# 5. FastAPI importable
cd ems-backend && source venv/bin/activate
python -c "from fastapi import FastAPI; print('FastAPI OK')"

# 6. Frontend dependencies installed
cd ../ems-frontend && ls node_modules | wc -l
# Expected: a number greater than 100
```

If all checks pass, your environment is ready. Proceed to **Phase 2: Implementation**.

---

*Next: [02_implementation.md](02_implementation.md)*