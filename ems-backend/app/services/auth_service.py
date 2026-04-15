# datetime is used to calculate the token expiry time (current time + X minutes).
from datetime import datetime, timedelta

# python-jose is a library for working with JWT (JSON Web Tokens).
# JWTError is raised when a token is invalid or tampered with.
# jwt provides encode() to create tokens and decode() to verify and read them.
from jose import JWTError, jwt

# passlib is a password hashing library. CryptContext manages hashing schemes
# so we never have to call the underlying algorithm (bcrypt) directly.
from passlib.context import CryptContext

# Import app settings to access SECRET_KEY, ALGORITHM, and token expiry duration.
from app.config import settings

# Configure passlib to use bcrypt as the hashing algorithm.
# bcrypt is a slow, adaptive algorithm specifically designed for passwords — its
# slowness makes brute-force attacks impractical even with powerful hardware.
# deprecated="auto" tells passlib to automatically re-hash any passwords stored
# with an older/weaker scheme if you ever change algorithms in the future.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Store passwords only as bcrypt hashes — NFR-8."""
    # pwd_context.hash() generates a random salt, hashes the password with bcrypt,
    # and returns a single string that contains both the salt and the hash.
    # The salt means two users with the same password will have different hashes.
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Hashing is one-way — you can't reverse it to recover the plain password.
    # Instead, we re-hash the login attempt and compare it against the stored hash.
    # pwd_context.verify() handles the salt extraction and comparison securely.
    # Returns True if the passwords match, False otherwise.
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    # Copy the payload so we don't mutate the original dict passed by the caller.
    to_encode = data.copy()

    # Calculate when this token should expire (current UTC time + configured minutes).
    # Using UTC avoids timezone-related bugs when the server and client are in
    # different regions.
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add the expiry time to the payload under the standard JWT claim key "exp".
    # When the token is later decoded, the JWT library checks "exp" automatically
    # and raises an error if the token has expired.
    to_encode.update({"exp": expire})

    # Encode the payload into a signed JWT string.
    # The SECRET_KEY is used to create a cryptographic signature so the server
    # can later verify that the token hasn't been tampered with.
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        # Decode and verify the JWT. This checks:
        #   1. The signature — was this token signed with our SECRET_KEY?
        #   2. The expiry — has the "exp" time passed?
        # If both checks pass, the original payload dict is returned.
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        # JWTError covers all failure cases: invalid signature, expired token,
        # malformed token string, etc. Returning None lets the caller decide
        # how to handle it (the router will typically raise a 401 Unauthorized).
        return None
