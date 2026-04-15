# fileConfig sets up Python's logging system using the settings defined in alembic.ini,
# so Alembic can print progress/error messages to the console.
from logging.config import fileConfig

# engine_from_config builds a SQLAlchemy engine using values from alembic.ini.
from sqlalchemy import engine_from_config

# pool controls how database connections are managed/reused.
from sqlalchemy import pool

# context is Alembic's runtime object — it holds configuration and drives migrations.
from alembic import context

# The Alembic Config object, which gives us access to values in alembic.ini
# (e.g. the database URL under the [alembic] section).
config = context.config

# Configure Python's logging using the [loggers] / [handlers] sections in alembic.ini.
# This enables colour-coded output like "Running upgrade abc123 -> def456".
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import our SQLAlchemy Base so Alembic knows the full schema of our application.
# `Base.metadata` contains descriptions of every table defined in our models.
from app.database import Base

# Importing the models package ensures every model module is executed, which
# registers each table with Base.metadata. Without this, Alembic would not
# "see" those tables when generating or comparing migrations.
from app import models  # ensure all models are imported

# Tell Alembic which metadata object describes our target schema.
# When you run `alembic revision --autogenerate`, Alembic compares this metadata
# against the live database to detect what has changed (added/removed tables, columns, etc.).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Offline mode generates SQL statements as plain text rather than executing them
    # against a live database. Useful for reviewing changes before applying them,
    # or for environments where a live DB connection is not available.
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        # literal_binds=True renders query parameters as literal values in the SQL output
        # instead of placeholders like ":param", making the generated SQL easier to read.
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # Begin a transaction block and run all pending migration steps inside it.
    # If any step fails, the whole transaction is rolled back (nothing is half-applied).
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Online mode connects to the live database and executes migration SQL directly.
    # This is what normally runs when you do `alembic upgrade head`.

    # Build a SQLAlchemy engine from the [alembic] section of alembic.ini.
    # NullPool disables connection pooling — each migration gets a fresh connection
    # and it is closed immediately after. This is recommended for migration scripts.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",   # only pick up keys that start with "sqlalchemy."
        poolclass=pool.NullPool,
    )

    # Open a connection to the database and bind it to the Alembic context.
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # Run all pending migrations inside a single transaction.
        with context.begin_transaction():
            context.run_migrations()


# Entry point: Alembic calls this file and checks whether it was invoked in
# offline mode (e.g. `alembic upgrade head --sql`) or online mode (the default).
# The correct function is called automatically based on that flag.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

