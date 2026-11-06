from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.ingrediente import Ingrediente
from app.models.alternativa_ingrediente import AlternativaIngrediente


ALTERNATIVAS_INICIALES = [
    {
        "receta": "Ensalada de garbanzos",
        "original": "Garbanzos",
        "sustituto": "Lentejas",
        "cantidad": 150,
        "unidad": "g",
    },
]

# Recetas que contienen leche de origen animal.
RECETAS_CON_LECHE = [
    "Avena con banana",
    "Avena con manzana",
    "Avena con almendras y banana",
    "Licuado de banana y avena",
    "Licuado de manzana y avena",
    "Licuado de frutillas y banana",
    "Porridge de avena y pera",
]

# Alternativas vegetales.
BEBIDAS_VEGETALES = [
    "Leche de coco",
    "Leche de almendras",
    "Bebida de avena",
]

# Asociar cada alternativa a cada receta.
for receta in RECETAS_CON_LECHE:
    for sustituto in BEBIDAS_VEGETALES:
        ALTERNATIVAS_INICIALES.append(
            {
                "receta": receta,
                "original": "Leche",
                "sustituto": sustituto,
                "cantidad": 200,
                "unidad": "ml",
            }
        )


def main():
    with SessionLocal() as db:
        for datos in ALTERNATIVAS_INICIALES:

            posicion = db.scalar(
                select(RecetaIngrediente)
                .join(Receta)
                .join(
                    Ingrediente,
                    RecetaIngrediente.ingrediente_id == Ingrediente.id,
                )
                .where(
                    Receta.nombre == datos["receta"],
                    Ingrediente.nombre == datos["original"],
                )
            )

            if posicion is None:
                raise ValueError(
                    f"No se encontró el ingrediente "
                    f"'{datos['original']}' en '{datos['receta']}'. "
                    "Ejecutá primero seed_catalogos y seed_recetas."
                )

            sustituto = db.scalar(
                select(Ingrediente).where(
                    Ingrediente.nombre == datos["sustituto"]
                )
            )

            if sustituto is None:
                raise ValueError(
                    f"No existe el ingrediente alternativo "
                    f"'{datos['sustituto']}'."
                )

            existente = db.scalar(
                select(AlternativaIngrediente).where(
                    AlternativaIngrediente.receta_ingrediente_id == posicion.id,
                    AlternativaIngrediente.ingrediente_alternativo_id == sustituto.id,
                )
            )

            if existente is not None:
                continue

            db.add(
                AlternativaIngrediente(
                    receta_ingrediente_id=posicion.id,
                    ingrediente_alternativo_id=sustituto.id,
                    cantidad=datos["cantidad"],
                    unidad=datos["unidad"],
                )
            )

        db.commit()

    print("Carga inicial de alternativas finalizada.")


if __name__ == "__main__":
    main()
