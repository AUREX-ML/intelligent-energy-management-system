# APIRouter groups related endpoints together. This router handles everything
# under the "/api/v1/users" prefix (set in main.py).
# Depends is FastAPI's dependency injection system — it lets us automatically
# provide things like a database session to every route that needs one.
# HTTPException lets us return a proper HTTP error response (e.g. 404 Not Found).
# status provides readable names for HTTP status codes (e.g. status.HTTP_404_NOT_FOUND = 404).
from fastapi import APIRouter, Depends, HTTPException, status

# AsyncSession is an async-compatible database session from SQLAlchemy.
# "async" means the route can wait for database I/O without blocking other requests.
from sqlalchemy.ext.asyncio import AsyncSession

# get_db is a dependency that opens a database session and closes it after the request.
from app.database import get_db

# Pydantic schemas define the shape of data coming IN (UserCreate, UserUpdate)
# and going OUT (UserRead) for this resource.
# FastAPI uses them to validate request bodies and serialize response data automatically.
from app.schemas import UserCreate, UserRead, UserUpdate

# UserService contains all the business logic for user operations (query, create, etc.)
# Keeping logic in a service file instead of the router keeps routes clean and testable.
from app.services.user_service import UserService

# Create the router instance. main.py registers this with app.include_router().
router = APIRouter()


# GET /api/v1/users/
# Returns a list of all users.
# `response_model=list[UserRead]` tells FastAPI to serialise the return value
# using the UserRead schema and strip any fields not included in it (e.g. passwords).
@router.get("/", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db)):
    # Depends(get_db) automatically injects an open DB session into `db`.
    return await UserService.get_all(db)


# GET /api/v1/users/{user_id}
# Returns a single user by their ID. The {user_id} part of the path is a
# "path parameter" — FastAPI extracts it from the URL and passes it as an argument.
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        # If no user was found, respond with 404 Not Found instead of returning None.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# POST /api/v1/users/
# Creates a new user from the JSON body sent by the client.
# `payload: UserCreate` tells FastAPI to parse the request body and validate it
# against the UserCreate schema. If the body is missing or invalid, FastAPI
# automatically returns a 422 Unprocessable Entity error.
# `status_code=201` means "Created" — more accurate than the default 200 "OK"
# because a new resource was created.
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService.create(db, payload)


# PATCH /api/v1/users/{user_id}
# Partially updates an existing user. PATCH (vs PUT) means only the fields
# included in the request body are updated; everything else stays the same.
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: str, payload: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await UserService.update(db, user_id, payload)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# DELETE /api/v1/users/{user_id}
# Deletes a user by ID.
# `status_code=204` means "No Content" — the request succeeded but there is
# nothing to return (the resource no longer exists). FastAPI will send an empty body.
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await UserService.delete(db, user_id)
    if not deleted:
        # If the service couldn't find the user to delete, return 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

