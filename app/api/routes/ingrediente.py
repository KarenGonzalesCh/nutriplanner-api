
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingrediente import IngredienteResponse
from app.services.ingrediente import IngredienteService


router = APIRouter(
    prefix="/ingredientes",
    tags=["Catálogos Alimentarios"],
)


@router.get("", response_model=list[IngredienteResponse])
def listar_ingredientes(db: Session = Depends(get_db)):
    servicio = IngredienteService(db)

    return servicio.listar()
