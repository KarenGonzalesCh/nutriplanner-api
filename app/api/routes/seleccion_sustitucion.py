
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import obtener_cuenta_actual
from app.db.session import get_db
from app.models.cuenta import Cuenta

from app.schemas.seleccion_sustitucion import (
    SeleccionarSustitucionRequest,
    SustitucionGuardadaResponse,
)

from app.services.seleccion_sustitucion import (
    SeleccionSustitucionService,
    RecetaNoDisponibleError,
    IngredienteNoEncontradoError,
    PerfilNoConfiguradoError,
    AlternativaNoValidaError,
)


router = APIRouter(
    prefix="/recetas",
    tags=["Sustituciones seleccionadas"],
)


def convertir_error(error: Exception) -> HTTPException:
    """Convertir errores del servicio en respuestas HTTP."""

    if isinstance(
        error,
        (RecetaNoDisponibleError, IngredienteNoEncontradoError),
    ):
        codigo = HTTPStatus.NOT_FOUND

    elif isinstance(error, PerfilNoConfiguradoError):
        codigo = HTTPStatus.CONFLICT

    elif isinstance(error, AlternativaNoValidaError):
        codigo = HTTPStatus.BAD_REQUEST

    else:
        codigo = HTTPStatus.INTERNAL_SERVER_ERROR

    return HTTPException(
        status_code=codigo,
        detail=str(error),
    )


@router.get(
    "/{receta_id}/sustituciones",
    response_model=list[SustitucionGuardadaResponse],
)
def listar_sustituciones(
    receta_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = SeleccionSustitucionService(db)

    try:
        return servicio.listar(cuenta_actual.id, receta_id)

    except (
        RecetaNoDisponibleError,
        PerfilNoConfiguradoError,
    ) as error:
        raise convertir_error(error) from error


@router.put(
    "/{receta_id}/sustituciones/{receta_ingrediente_id}",
    response_model=SustitucionGuardadaResponse,
)
def guardar_sustitucion(
    receta_id: int,
    receta_ingrediente_id: int,
    datos: SeleccionarSustitucionRequest,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = SeleccionSustitucionService(db)

    try:
        return servicio.guardar(
            cuenta_id=cuenta_actual.id,
            receta_id=receta_id,
            receta_ingrediente_id=receta_ingrediente_id,
            alternativa_id=datos.alternativa_id,
        )

    except (
        RecetaNoDisponibleError,
        IngredienteNoEncontradoError,
        PerfilNoConfiguradoError,
        AlternativaNoValidaError,
    ) as error:
        raise convertir_error(error) from error


@router.delete(
    "/{receta_id}/sustituciones/{receta_ingrediente_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
def eliminar_sustitucion(
    receta_id: int,
    receta_ingrediente_id: int,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = SeleccionSustitucionService(db)

    try:
        eliminada = servicio.eliminar(
            cuenta_id=cuenta_actual.id,
            receta_id=receta_id,
            receta_ingrediente_id=receta_ingrediente_id,
        )

    except (
        RecetaNoDisponibleError,
        IngredienteNoEncontradoError,
    ) as error:
        raise convertir_error(error) from error

    if not eliminada:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No existe una sustitución guardada",
        )
