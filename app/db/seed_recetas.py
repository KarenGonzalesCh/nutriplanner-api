
from sqlalchemy import select

from app.core.enums import NivelDificultad, TipoComida
from app.db.session import SessionLocal
from app.models.ingrediente import Ingrediente
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.receta_tipo_comida import RecetaTipoComida


RECETAS_INICIALES = [
    {
        "nombre": "Avena con banana",
        "pasos": "Calentar la leche, agregar la avena y servir con banana cortada.",
        "tiempo_preparacion": 10,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Avena", 50, "g"),
            ("Banana", 1, "unidad"),
            ("Leche", 200, "ml"),
        ],
    },
    {
        "nombre": "Arroz con pollo",
        "pasos": "Cocinar el arroz. Cocinar el pollo con aceite de oliva y servir juntos.",
        "tiempo_preparacion": 35,
        "dificultad": NivelDificultad.INTERMEDIO,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Arroz", 150, "g"),
            ("Pollo", 200, "g"),
            ("Aceite de oliva", 15, "ml"),
        ],
    },
    {
        "nombre": "Ensalada de garbanzos",
        "pasos": "Cocinar los garbanzos si es necesario. Cortar las verduras y mezclar.",
        "tiempo_preparacion": 20,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Garbanzos", 150, "g"),
            ("Tomate", 1, "unidad"),
            ("Zanahoria", 1, "unidad"),
        ],
    },
    {
        "nombre": "Omelette de espinaca",
        "pasos": "Batir los huevos, agregar espinaca y queso, y cocinar en sartén.",
        "tiempo_preparacion": 15,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.ALMUERZO],
        "ingredientes": [
            ("Huevo", 2, "unidad"),
            ("Espinaca", 50, "g"),
            ("Queso", 30, "g"),
        ],
    },
    {
        "nombre": "Merluza con arroz",
        "pasos": "Cocinar la merluza y acompañar con arroz hervido.",
        "tiempo_preparacion": 30,
        "dificultad": NivelDificultad.INTERMEDIO,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Merluza", 200, "g"),
            ("Arroz", 150, "g"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
]


def main():
    with SessionLocal() as db:
        ingredientes = {
            ingrediente.nombre: ingrediente.id
            for ingrediente in db.scalars(
                select(Ingrediente)
            ).all()
        }

        for datos in RECETAS_INICIALES:
            receta_existente = db.scalar(
                select(Receta).where(Receta.nombre == datos["nombre"])
            )

            # Si ya existe, completar porciones_base solo si falta.
            if receta_existente is not None:
                if receta_existente.porciones_base is None:
                    receta_existente.porciones_base = datos["porciones_base"]
                continue

            for nombre, _, _ in datos["ingredientes"]:
                if nombre not in ingredientes:
                    raise ValueError(
                        f"Falta el ingrediente '{nombre}'. Ejecutá primero seed_catalogos."
                    )

            receta = Receta(
                nombre=datos["nombre"],
                pasos=datos["pasos"],
                tiempo_preparacion=datos["tiempo_preparacion"],
                dificultad=datos["dificultad"],
                porciones_base=datos["porciones_base"],
                info_nutricional=None,
                activa=True,
            )

            for tipo in datos["tipos_comida"]:
                receta.tipos_comida.append(
                    RecetaTipoComida(tipo_comida=tipo)
                )

            for nombre, cantidad, unidad in datos["ingredientes"]:
                receta.ingredientes.append(
                    RecetaIngrediente(
                        ingrediente_id=ingredientes[nombre],
                        cantidad=cantidad,
                        unidad=unidad,
                    )
                )

            db.add(receta)

        db.commit()

    print("Carga inicial de recetas finalizada.")


if __name__ == "__main__":
    main()
