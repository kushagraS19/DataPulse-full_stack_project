from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import settings
from app.models.base import Base

# Import every model so Alembic can detect all tables.
from app.models.user_model import User
from app.models.workspace_model import Workspace
from app.models.project_model import Project
from app.models.dataset_model import Dataset
from app.models.dataset_row_model import DatasetRow
from app.models.dashboard_model import Dashboard
from app.models.chart_model import Chart
from app.models.email_verification_otp_model import EmailVerificationOTP
from app.models.login_attempt_model import LoginAttempt
from app.models.password_change_otp_model import PasswordChangeOTP
from app.models.password_reset_otp_model import PasswordResetOTP
from app.models.refresh_token_model import RefreshToken
from app.models.audit_log_model import AuditLog


config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("%", "%%"),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(
    object_,
    name,
    type_,
    reflected,
    compare_to,
):
    """
    Ignore dynamically generated dataset tables during Alembic comparison.

    These tables store uploaded CSV data and are managed by DataPulse,
    not by static SQLAlchemy model definitions.
    """
    if type_ == "table" and name and name.startswith("dataset_") and name.endswith("_data"):
        return False

    return True


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure and run migrations using a database connection."""

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations with a live database connection."""

    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()