
from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.models.cuenta import Cuenta
from app.models.perfil_alimentario import PerfilAlimentario
from app.models.categoria_alimento import CategoriaAlimento
from app.models.ingrediente import Ingrediente
from app.models.alergia import Alergia
from app.models.alergia_ingrediente import AlergiaIngrediente

def test_creacion_tablas():
    """Verifica que se creen las tablas iniciales."""

    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        tablas = inspect(engine).get_table_names()

        assert "cuenta" in tablas
        assert "perfil_alimentario" in tablas
    finally:
        engine.dispose()



def test_crear_cuenta_con_perfil():
    """Verifica que una cuenta pueda guardar su perfil alimentario."""

    from sqlalchemy.orm import Session
    from app.core.enums import Rol, NivelDificultad

    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            cuenta = Cuenta(
                nombre_usuario="usuario_prueba",
                correo="prueba@example.com",
                password_hash="hash_simulado_para_test",
                rol=Rol.USUARIO
            )

            perfil = PerfilAlimentario(
                nivel_culinario=NivelDificultad.PRINCIPIANTE
            )

            cuenta.perfil_alimentario = perfil

            session.add(cuenta)
            session.commit()

            cuenta_id = cuenta.id

        with Session(engine) as session:
            cuenta_guardada = session.get(Cuenta, cuenta_id)

            assert cuenta_guardada is not None
            assert cuenta_guardada.nombre_usuario == "usuario_prueba"
            assert cuenta_guardada.perfil_alimentario is not None
            assert (
                cuenta_guardada.perfil_alimentario.nivel_culinario
                == NivelDificultad.PRINCIPIANTE
            )
    finally:
        engine.dispose()


def test_cuenta_no_puede_tener_dos_perfiles():
    """Verifica que una cuenta no pueda tener dos perfiles."""

    import pytest
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import Session
    from app.core.enums import NivelDificultad, Rol

    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            cuenta = Cuenta(
                nombre_usuario="usuario_unico",
                correo="unico@example.com",
                password_hash="hash_simulado_para_test",
                rol=Rol.USUARIO
            )

            session.add(cuenta)
            session.commit()

            perfil_1 = PerfilAlimentario(
                cuenta_id=cuenta.id,
                nivel_culinario=NivelDificultad.PRINCIPIANTE
            )

            perfil_2 = PerfilAlimentario(
                cuenta_id=cuenta.id,
                nivel_culinario=NivelDificultad.INTERMEDIO
            )

            session.add_all([perfil_1, perfil_2])

            with pytest.raises(IntegrityError):
                session.commit()

            session.rollback()
    finally:
        engine.dispose()


def test_categoria_con_ingredientes():
    """Verifica que una categoría pueda tener varios ingredientes."""

    from sqlalchemy.orm import Session

    from app.models.categoria_alimento import CategoriaAlimento
    from app.models.ingrediente import Ingrediente

    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            categoria = CategoriaAlimento(nombre="Verduras")

            categoria.ingredientes = [
                Ingrediente(nombre="Zanahoria"),
                Ingrediente(nombre="Tomate"),
                Ingrediente(nombre="Cebolla"),
            ]

            session.add(categoria)
            session.commit()

            categoria_id = categoria.id

        with Session(engine) as session:
            categoria_guardada = session.get(
                CategoriaAlimento, categoria_id
            )

            assert categoria_guardada is not None
            assert categoria_guardada.nombre == "Verduras"
            assert len(categoria_guardada.ingredientes) == 3

            nombres = {
                ingrediente.nombre
                for ingrediente in categoria_guardada.ingredientes
            }

            assert nombres == {"Zanahoria", "Tomate", "Cebolla"}

            for ingrediente in categoria_guardada.ingredientes:
                assert ingrediente.categoria_id == categoria_id

    finally:
        engine.dispose()



def test_no_permitir_ingredientes_duplicados():
    """Verifica que no existan ingredientes con el mismo nombre."""

    import pytest
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import Session

    from app.models.categoria_alimento import CategoriaAlimento
    from app.models.ingrediente import Ingrediente

    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            categoria = CategoriaAlimento(nombre="Verduras")
            session.add(categoria)
            session.flush()

            ingrediente_1 = Ingrediente(
                nombre="Tomate",
                categoria_id=categoria.id
            )

            ingrediente_2 = Ingrediente(
                nombre="Tomate",
                categoria_id=categoria.id
            )

            session.add_all([ingrediente_1, ingrediente_2])

            with pytest.raises(IntegrityError):
                session.commit()

            session.rollback()
    finally:
        engine.dispose()



def test_alergia_con_varios_ingredientes():
    """Verifica la relación muchos a muchos entre alergias e ingredientes."""

    from sqlalchemy.orm import Session

    from app.models.categoria_alimento import CategoriaAlimento
    from app.models.ingrediente import Ingrediente
    from app.models.alergia import Alergia
    from app.models.alergia_ingrediente import AlergiaIngrediente

    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            categoria = CategoriaAlimento(nombre="Lacteos")

            leche = Ingrediente(nombre="Leche", categoria=categoria)
            queso = Ingrediente(nombre="Queso", categoria=categoria)

            alergia = Alergia(nombre="Alergia a la leche")
            alergia.ingredientes = [leche, queso]

            session.add(alergia)
            session.commit()

            alergia_id = alergia.id

        with Session(engine) as session:
            alergia_guardada = session.get(Alergia, alergia_id)

            assert alergia_guardada is not None
            assert len(alergia_guardada.ingredientes) == 2

            nombres = {
                ingrediente.nombre
                for ingrediente in alergia_guardada.ingredientes
            }

            assert nombres == {"Leche", "Queso"}

            for ingrediente in alergia_guardada.ingredientes:
                assert alergia_guardada in ingrediente.alergias

    finally:
        engine.dispose()



def test_perfil_con_varias_alergias():
    """Verifica que un perfil pueda tener varias alergias."""

    import app.models
    from sqlalchemy.orm import Session

    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            cuenta = Cuenta(
                nombre_usuario="usuario_alergias",
                correo="alergias@example.com",
                password_hash="hash_de_prueba"
            )

            perfil = PerfilAlimentario(cuenta=cuenta)

            alergia_leche = Alergia(nombre="Alergia a la leche")
            alergia_huevo = Alergia(nombre="Alergia al huevo")

            perfil.alergias = [alergia_leche, alergia_huevo]

            session.add(perfil)
            session.commit()

            perfil_id = perfil.id

        # Abrimos otra sesión para verificar los datos guardados.
        with Session(engine) as session:
            perfil_guardado = session.get(
                PerfilAlimentario, perfil_id
            )

            assert perfil_guardado is not None
            assert len(perfil_guardado.alergias) == 2

            nombres = {
                alergia.nombre
                for alergia in perfil_guardado.alergias
            }

            assert nombres == {
                "Alergia a la leche",
                "Alergia al huevo"
            }

            # Verificamos también la relación inversa.
            for alergia in perfil_guardado.alergias:
                assert perfil_guardado in alergia.perfiles_alimentarios

    finally:
        engine.dispose()
