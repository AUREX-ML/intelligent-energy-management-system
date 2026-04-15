# Optional is a type hint meaning a function can return either a value OR None.
# e.g. Optional[User] means "a User object, or None if not found".
from typing import Optional

# `select` builds a SQL SELECT query using Python syntax instead of raw SQL strings.
# e.g. select(User) generates "SELECT * FROM users"
from sqlalchemy import select

# AsyncSession is an async-aware database session. Using `await` with it means
# the server can handle other requests while waiting for the database to respond.
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# hash_password converts a plain-text password into a secure one-way hash
# before storing it. We never store raw passwords in the database.
from app.utils.security import hash_password


# UserService groups all database operations related to users in one place.
# Keeping this logic out of the router makes it easier to test and reuse.
#
# Every method is a @staticmethod, meaning you call it as UserService.get_all(db)
# rather than needing to create a UserService() instance first.
class UserService:

    @staticmethod
    async def get_all(db: AsyncSession) -> list[User]:
        # Build and execute "SELECT * FROM users".
        result = await db.execute(select(User))
        # .scalars() unwraps the raw SQLAlchemy Row objects into plain User instances.
        # .all() collects them into a Python list.
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        # Build "SELECT * FROM users WHERE id = :user_id" and execute it.
        result = await db.execute(select(User).where(User.id == user_id))
        # scalar_one_or_none() returns the single matching User, or None if not found.
        # It also raises an error if the query unexpectedly returns more than one row.
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, payload: UserCreate) -> User:
        # Build a new User ORM object from the validated request data.
        # The plain-text password from the payload is hashed before being stored.
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        # Stage the new user: tells SQLAlchemy to include it in the next commit.
        db.add(user)
        # Write the staged changes to the database permanently.
        await db.commit()
        # Refresh reloads the user object from the database so that any
        # database-generated values (e.g. auto-assigned id, created_at timestamp)
        # are populated on the Python object before we return it.
        await db.refresh(user)
        return user

    @staticmethod
    async def update(db: AsyncSession, user_id: str, payload: UserUpdate) -> Optional[User]:
        # First, fetch the existing user. Return None if they don't exist.
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None

        # model_dump() converts the Pydantic schema to a plain Python dict.
        # exclude_unset=True means only fields the client actually sent are included —
        # fields left out of the request body are NOT overwritten with None/defaults.
        update_data = payload.model_dump(exclude_unset=True)

        # If the client sent a new password, hash it before storing it.
        # .pop("password") removes the plain-text key so it is never written to the DB.
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        # Apply each updated field to the User object using setattr.
        # e.g. setattr(user, "full_name", "Jane") is the same as user.full_name = "Jane"
        for field, value in update_data.items():
            setattr(user, field, value)

        # Persist the changes and refresh the object to get the latest DB values.
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete(db: AsyncSession, user_id: str) -> bool:
        # Fetch the user first so we can confirm they exist before attempting deletion.
        user = await UserService.get_by_id(db, user_id)
        if not user:
            # Return False so the router knows to send a 404 response.
            return False
        # Mark the user for deletion and commit the transaction to the database.
        await db.delete(user)
        await db.commit()
        # Return True so the router knows the deletion succeeded.
        return True

