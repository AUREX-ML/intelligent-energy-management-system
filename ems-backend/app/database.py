# SQLAlchemy is the ORM (Object-Relational Mapper) we use to interact with the database
# using Python classes and objects instead of raw SQL queries.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Import our app's settings, which include the DATABASE_URL connection string.
from app.config import settings

# The engine is the low-level connection to the database.
# `pool_pre_ping=True` tests each connection before using it, so stale/broken
# connections are automatically recycled instead of causing errors.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionLocal is a factory that creates new database session objects.
# - autocommit=False: changes are NOT saved until we explicitly call db.commit()
# - autoflush=False:  SQLAlchemy won't automatically send pending changes to the DB
#                     before every query — this gives us more control over transactions
# - bind=engine:      tells the session which database engine/connection to use
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base is the parent class that all our database models (tables) will inherit from.
# SQLAlchemy uses it to track which classes map to which database tables.
class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency to inject DB session into route handlers."""
    # Open a new database session for this request.
    db = SessionLocal()
    try:
        # `yield` hands the session to the route handler that requested it.
        # Everything before `yield` runs before the route, everything after runs after.
        yield db
    finally:
        # Always close the session when the request is done, even if an error occurred.
        # This returns the connection back to the pool so it can be reused.
        db.close()