from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Engine

from application import db
from application.app import factory
from application.settings import Settings

config = context.config
fileConfig(config.config_file_name)
target_metadata = db.Base.metadata
container = factory().state.injector


def run_migrations_offline():
    context.configure(
        url=container.get(Settings).database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = container.get(Engine)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
