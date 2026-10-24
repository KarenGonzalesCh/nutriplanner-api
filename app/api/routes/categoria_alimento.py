
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.categoria_alimento import CategoriaAlimentoResponse
from app.services.categoria_alimento import CategoriaAlimentoService


router = APIRouter(
    prefix="/categorias-alimento",
    tags=["Catálogos Alimentarios"],
)


@router.get("", response_model=list[CategoriaAlimentoResponse])
def listar_categorias(db: Session = Depends(get_db)):
    servicio = CategoriaAlimentoService(db)

    return servicio.listar()
