
"""Cargar alternativas vegetales para recetas con leche.

Revision ID: 2d481a823123
Revises: 1a77b668d21f
"""

from alembic import op
import sqlalchemy as sa


revision = "2d481a823123"
down_revision = "1a77b668d21f"
branch_labels = None
depends_on = None


BEBIDAS_VEGETALES = {
    "Leche de coco": "Frutas",
    "Leche de almendras": "Frutos secos y semillas",
    "Bebida de avena": "Cereales",
}

RECETAS_CON_LECHE = [
    "Avena con banana",
    "Avena con manzana",
    "Avena con almendras y banana",
    "Licuado de banana y avena",
    "Licuado de manzana y avena",
    "Licuado de frutillas y banana",
    "Porridge de avena y pera",
]


def buscar_id(conexion, tabla, nombre):
    return conexion.execute(
        sa.select(tabla.c.id).where(tabla.c.nombre == nombre)
    ).scalar_one_or_none()


def upgrade() -> None:
    conexion = op.get_bind()

    categorias = sa.table(
        "categoria_alimento",
        sa.column("id", sa.Integer),
        sa.column("nombre", sa.String),
    )

    ingredientes = sa.table(
        "ingrediente",
        sa.column("id", sa.Integer),
        sa.column("nombre", sa.String),
        sa.column("categoria_id", sa.Integer),
    )

    alergias = sa.table(
        "alergia",
        sa.column("id", sa.Integer),
        sa.column("nombre", sa.String),
    )

    alergia_ingrediente = sa.table(
        "alergia_ingrediente",
        sa.column("alergia_id", sa.Integer),
        sa.column("ingrediente_id", sa.Integer),
    )

    recetas = sa.table(
        "receta",
        sa.column("id", sa.Integer),
        sa.column("nombre", sa.String),
    )

    posiciones = sa.table(
        "receta_ingrediente",
        sa.column("id", sa.Integer),
        sa.column("receta_id", sa.Integer),
        sa.column("ingrediente_id", sa.Integer),
    )

    alternativas = sa.table(
        "alternativa_ingrediente",
        sa.column("id", sa.Integer),
        sa.column("receta_ingrediente_id", sa.Integer),
        sa.column("ingrediente_alternativo_id", sa.Integer),
        sa.column("cantidad", sa.Float),
        sa.column("unidad", sa.String),
    )

    # 1. Registrar las tres bebidas vegetales.
    for nombre, nombre_categoria in BEBIDAS_VEGETALES.items():
        categoria_id = buscar_id(
            conexion, categorias, nombre_categoria
        )

        if categoria_id is None:
            raise ValueError(
                f"No existe la categoría: {nombre_categoria}"
            )

        ingrediente_id = buscar_id(
            conexion, ingredientes, nombre
        )

        if ingrediente_id is None:
            conexion.execute(
                sa.insert(ingredientes).values(
                    nombre=nombre,
                    categoria_id=categoria_id,
                )
            )

    # 2. Registrar la alergia de la leche de almendras.
    almendras_id = buscar_id(
        conexion, ingredientes, "Leche de almendras"
    )
    alergia_id = buscar_id(
        conexion, alergias, "Frutos secos"
    )

    if alergia_id is None:
        raise ValueError(
            "No existe la alergia Frutos secos"
        )

    relacion_existente = conexion.execute(
        sa.select(alergia_ingrediente.c.ingrediente_id)
        .where(
            alergia_ingrediente.c.alergia_id == alergia_id,
            alergia_ingrediente.c.ingrediente_id == almendras_id,
        )
    ).first()

    if relacion_existente is None:
        conexion.execute(
            sa.insert(alergia_ingrediente).values(
                alergia_id=alergia_id,
                ingrediente_id=almendras_id,
            )
        )

    # 3. Asociar las alternativas a las siete recetas.
    leche_id = buscar_id(
        conexion, ingredientes, "Leche"
    )

    if leche_id is None:
        raise ValueError("No existe el ingrediente Leche")

    for nombre_receta in RECETAS_CON_LECHE:
        receta_id = buscar_id(
            conexion, recetas, nombre_receta
        )

        if receta_id is None:
            raise ValueError(
                f"No existe la receta: {nombre_receta}"
            )

        posicion_id = conexion.execute(
            sa.select(posiciones.c.id)
            .where(
                posiciones.c.receta_id == receta_id,
                posiciones.c.ingrediente_id == leche_id,
            )
        ).scalar_one_or_none()

        if posicion_id is None:
            raise ValueError(
                f"No se encontró Leche en {nombre_receta}"
            )

        for nombre_alternativa in BEBIDAS_VEGETALES:
            alternativa_id = buscar_id(
                conexion, ingredientes, nombre_alternativa
            )

            existente = conexion.execute(
                sa.select(alternativas.c.id)
                .where(
                    alternativas.c.receta_ingrediente_id
                    == posicion_id,
                    alternativas.c.ingrediente_alternativo_id
                    == alternativa_id,
                )
            ).scalar_one_or_none()

            if existente is None:
                conexion.execute(
                    sa.insert(alternativas).values(
                        receta_ingrediente_id=posicion_id,
                        ingrediente_alternativo_id=alternativa_id,
                        cantidad=200.0,
                        unidad="ml",
                    )
                )


def downgrade() -> None:
    # Conservamos los datos para evitar borrar ingredientes
    # o alternativas que puedan estar siendo utilizados.
    pass
