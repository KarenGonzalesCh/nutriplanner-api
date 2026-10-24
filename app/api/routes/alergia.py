
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alergia import AlergiaResponse
from app.services.alergia import AlergiaService


router = APIRouter(
    prefix="/alergias",
    tags=["Catálogos Alimentarios"],
)


@router.get("", response_model=list[AlergiaResponse])
def listar_alergias(db: Session = Depends(get_db)):
    servicio = AlergiaService(db)

    return servicio.listar()
