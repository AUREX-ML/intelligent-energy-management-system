# pydantic-settings lets us define app configuration as a Python class.
# It automatically reads values from environment variables or a `.env` file,
# and validates that each value has the correct type.
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    # Full connection string for SQLAlchemy, e.g.:
    # "postgresql://user:password@localhost:5432/ems_db"
    # Must be set in the .env file — no default is provided, so the app will
    # refuse to start if this is missing.
    DATABASE_URL: str

    # --- Authentication (JWT) ---
    # A long, random secret string used to sign JWT tokens. Keep this private!
    # If an attacker learns this value they can forge valid login tokens.
    SECRET_KEY: str

    # The hashing algorithm used when signing JWT tokens.
    # HS256 (HMAC + SHA-256) is the standard choice for most APIs.
    ALGORITHM: str = "HS256"

    # How many minutes a JWT access token stays valid before the user must log in again.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- MQTT Broker ---
    # MQTT is a lightweight messaging protocol used by IoT/sensor devices.
    # These two settings tell the app where to find the MQTT broker (message server).
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883   # 1883 is the default unencrypted MQTT port

    # --- Redis ---
    # Redis is an in-memory data store used here as a message broker for Celery
    # (our background task queue). The URL format is:
    # "redis://<host>:<port>/<db_number>"
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- App metadata ---
    app_name: str = "EMS-Backend"    # Human-readable name shown in API docs
    app_env: str = "development"     # Change to "production" when deploying
    debug: bool = True              # Set True locally for detailed error messages

    # --- SMTP (Email) ---
    # Settings for sending outgoing emails (e.g. alert notifications).
    # Leave blank if email sending is not needed.
    smtp_host: str = "smtp.gmail.com"        # Mail server hostname, e.g. "smtp.gmail.com"
    smtp_port: int = 587       # 587 is the standard port for STARTTLS encryption
    smtp_user: str = "ems-email@gmail.com"      # Email account username / sender address
    smtp_password: str = ""    # Email account password (store securely in .env!)

    # Tell pydantic-settings to read values from a `.env` file in the project root,
    # and silently ignore any extra keys in that file that aren't defined above.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Create a single shared instance of Settings.
# Import this `settings` object anywhere in the app to access configuration values.
settings = Settings()