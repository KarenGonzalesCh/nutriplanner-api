
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.db.base import Base

# Importamos los modelos para que SQLAlchemy registre sus tablas.
import app.models.cuenta
import app.models.perfil_alimentario
import app.models.categoria_alimento
import app.models.ingrediente
import app.models.alergia
import app.models.alergia_ingrediente
import app.models.perfil_alergia
import app.models.perfil_categoria_evitada
import app.models.perfil_ingrediente_evitado
import app.models.receta
import app.models.receta_ingrediente
import app.models.receta_tipo_comida
import app.models.alternativa_ingrediente


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
