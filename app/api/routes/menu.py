
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import obtener_cuenta_actual
from app.db.session import get_db
from app.models.cuenta import Cuenta
from app.repositories.receta import RecetaRepository
from app.schemas.menu import GenerarMenuRequest, PropuestaMenuResponse
from app.services.generador_menu import (
    GeneradorMenuService,
    PerfilMenuRequeridoError,
)
from app.services.preparacion_menu import preparar_respuesta_menu


router = APIRouter(prefix="/menus", tags=["Menús"])


@router.post(
    "/generar",
    response_model=PropuestaMenuResponse,
    status_code=HTTPStatus.OK,
)
def generar_menu(
    datos: GenerarMenuRequest,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    """
    Genera una propuesta temporal de menú.

    No guarda el menú ni realiza sustituciones automáticas.
    """
    servicio = GeneradorMenuService(db)

    try:
        propuesta = servicio.generar(
            cuenta_id=cuenta_actual.id,
            cantidad_dias=datos.cantidad_dias,
            tipos_comida=datos.tipos_comida,
        )

        recetas = RecetaRepository(db).listar()

        return preparar_respuesta_menu(
            propuesta=propuesta,
            recetas=recetas,
            comensales=datos.comensales,
        )

    except PerfilMenuRequeridoError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        ) from error
