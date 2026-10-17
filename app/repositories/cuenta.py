
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cuenta import Cuenta


class CuentaRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, cuenta_id: int) -> Cuenta | None:
        return self.db.get(Cuenta, cuenta_id)

    def obtener_por_correo(self, correo: str) -> Cuenta | None:
        consulta = select(Cuenta).where(Cuenta.correo == correo)
        return self.db.scalar(consulta)

    def obtener_por_nombre_usuario(
        self, nombre_usuario: str
    ) -> Cuenta | None:
        consulta = select(Cuenta).where(
            Cuenta.nombre_usuario == nombre_usuario
        )
        return self.db.scalar(consulta)

    def crear(self, cuenta: Cuenta) -> Cuenta:
        self.db.add(cuenta)
        self.db.commit()
        self.db.refresh(cuenta)
        return cuenta
