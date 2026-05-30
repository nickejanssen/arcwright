from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    required_keys = (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )
    values = {key: os.getenv(key) for key in required_keys}
    missing = [key for key, value in values.items() if not value]
    if missing:
        missing_keys = ", ".join(missing)
        raise RuntimeError(
            "Database configuration is missing. Set DATABASE_URL or define "
            f"{missing_keys}."
        )

    return (
        "postgresql+asyncpg://"
        f"{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}"
        f"@{values['POSTGRES_HOST']}:{values['POSTGRES_PORT']}"
        f"/{values['POSTGRES_DB']}"
    )


def configure_database_url() -> str:
    database_url = get_database_url()
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return database_url


def run_migrations_offline() -> None:
    url = configure_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    configure_database_url()
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    assert isinstance(connectable, AsyncEngine)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
