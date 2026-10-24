
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.perfil_alimentario import PerfilAlimentario
from app.models.alergia import Alergia
from app.models.ingrediente import Ingrediente
from app.models.categoria_alimento import CategoriaAlimento


class PerfilAlimentarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_por_cuenta(
        self, cuenta_id: int
    ) -> PerfilAlimentario | None:

        consulta = (
            select(PerfilAlimentario)
            .where(PerfilAlimentario.cuenta_id == cuenta_id)
            .options(
                selectinload(PerfilAlimentario.alergias),
                selectinload(PerfilAlimentario.ingredientes_evitados),
                selectinload(PerfilAlimentario.categorias_evitadas),
            )
        )

        return self.db.scalar(consulta)

    def obtener_alergias(self, ids: list[int]) -> list[Alergia]:
        return list(
            self.db.scalars(
                select(Alergia).where(Alergia.id.in_(ids))
            ).all()
        )

    def obtener_ingredientes(self, ids: list[int]) -> list[Ingrediente]:
        return list(
            self.db.scalars(
                select(Ingrediente).where(Ingrediente.id.in_(ids))
            ).all()
        )

    def obtener_categorias(self, ids: list[int]) -> list[CategoriaAlimento]:
        return list(
            self.db.scalars(
                select(CategoriaAlimento).where(CategoriaAlimento.id.in_(ids))
            ).all()
        )

    def guardar(self, perfil: PerfilAlimentario) -> PerfilAlimentario:
        self.db.add(perfil)
        self.db.commit()
        self.db.refresh(perfil)
        return perfil
