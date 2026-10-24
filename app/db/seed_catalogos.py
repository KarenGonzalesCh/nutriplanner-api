
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.categoria_alimento import CategoriaAlimento
from app.models.alergia import Alergia
from app.models.ingrediente import Ingrediente

CATEGORIAS_INICIALES = [
    "Aceites y grasas",
    "Carnes",
    "Cereales",
    "Frutas",
    "Frutos secos y semillas",
    "Huevos",
    "Lácteos",
    "Legumbres",
    "Pescados y mariscos",
    "Verduras",
]

ALERGIAS_INICIALES = [
    "Huevo",
    "Leche",
    "Maní",
    "Frutos secos",
    "Soja",
    "Trigo",
    "Pescado",
    "Mariscos",
    "Sésamo",
]


INGREDIENTES_INICIALES = [
    ("Aceite de oliva", "Aceites y grasas"),
    ("Carne vacuna", "Carnes"),
    ("Pollo", "Carnes"),
    ("Arroz", "Cereales"),
    ("Avena", "Cereales"),
    ("Trigo", "Cereales"),
    ("Banana", "Frutas"),
    ("Manzana", "Frutas"),
    ("Almendra", "Frutos secos y semillas"),
    ("Maní", "Frutos secos y semillas"),
    ("Sésamo", "Frutos secos y semillas"),
    ("Huevo", "Huevos"),
    ("Leche", "Lácteos"),
    ("Queso", "Lácteos"),
    ("Garbanzos", "Legumbres"),
    ("Lentejas", "Legumbres"),
    ("Soja", "Legumbres"),
    ("Atún", "Pescados y mariscos"),
    ("Camarón", "Pescados y mariscos"),
    ("Merluza", "Pescados y mariscos"),
    ("Espinaca", "Verduras"),
    ("Tomate", "Verduras"),
    ("Zanahoria", "Verduras"),
]


ALERGIAS_POR_INGREDIENTE = {
    "Almendra": ["Frutos secos"],
    "Maní": ["Maní"],
    "Sésamo": ["Sésamo"],
    "Huevo": ["Huevo"],
    "Leche": ["Leche"],
    "Queso": ["Leche"],
    "Soja": ["Soja"],
    "Trigo": ["Trigo"],
    "Atún": ["Pescado"],
    "Merluza": ["Pescado"],
    "Camarón": ["Mariscos"],
}


def cargar_categorias(db):
    for nombre in CATEGORIAS_INICIALES:
        categoria_existente = db.scalar(
            select(CategoriaAlimento).where(
                CategoriaAlimento.nombre == nombre
            )
        )

        if categoria_existente is None:
            db.add(CategoriaAlimento(nombre=nombre))


def cargar_alergias(db):
    for nombre in ALERGIAS_INICIALES:
        alergia_existente = db.scalar(
            select(Alergia).where(
                Alergia.nombre == nombre
            )
        )

        if alergia_existente is None:
            db.add(Alergia(nombre=nombre))


def cargar_ingredientes(db):
    # Guardar las categorías pendientes para obtener sus IDs
    db.flush()

    categorias = {
        categoria.nombre: categoria.id
        for categoria in db.scalars(
            select(CategoriaAlimento)
        ).all()
    }

    for nombre, nombre_categoria in INGREDIENTES_INICIALES:
        ingrediente_existente = db.scalar(
            select(Ingrediente).where(
                Ingrediente.nombre == nombre
            )
        )

        if ingrediente_existente is None:
            db.add(
                Ingrediente(
                    nombre=nombre,
                    categoria_id=categorias[nombre_categoria],
                )
            )


def cargar_relaciones_alergias(db):
    # Guardar los registros pendientes para poder consultarlos
    db.flush()

    ingredientes = {
        ingrediente.nombre: ingrediente
        for ingrediente in db.scalars(
            select(Ingrediente)
        ).all()
    }

    alergias = {
        alergia.nombre: alergia
        for alergia in db.scalars(
            select(Alergia)
        ).all()
    }

    for nombre_ingrediente, nombres_alergias in ALERGIAS_POR_INGREDIENTE.items():
        ingrediente = ingredientes[nombre_ingrediente]

        for nombre_alergia in nombres_alergias:
            alergia = alergias[nombre_alergia]

            if alergia not in ingrediente.alergias:
                ingrediente.alergias.append(alergia)


def main():
    with SessionLocal() as db:
        cargar_categorias(db)
        cargar_alergias(db)
        cargar_ingredientes(db)
        cargar_relaciones_alergias(db)
        db.commit()

    print("Categorías alimentarias y alergias cargadas correctamente.")


if __name__ == "__main__":
    main()
