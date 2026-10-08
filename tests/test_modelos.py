
from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.models.cuenta import Cuenta
from app.models.perfil_alimentario import PerfilAlimentario


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
