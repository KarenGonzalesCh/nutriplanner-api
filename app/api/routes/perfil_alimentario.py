
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import obtener_cuenta_actual
from app.db.session import get_db
from app.models.cuenta import Cuenta
from app.models.perfil_alimentario import PerfilAlimentario

from app.schemas.perfil_alimentario import (
    PerfilAlimentarioCreate,
    PerfilAlimentarioResponse,
)

from app.services.perfil_alimentario import (
    PerfilAlimentarioService,
    PerfilYaExisteError,
    PerfilNoEncontradoError,
    CatalogoInvalidoError,
)


router = APIRouter(prefix="/perfil", tags=["Perfil Alimentario"])


def preparar_respuesta(
    perfil: PerfilAlimentario,
) -> PerfilAlimentarioResponse:
    return PerfilAlimentarioResponse(
        id=perfil.id,
        cuenta_id=perfil.cuenta_id,
        nivel_culinario=perfil.nivel_culinario,
        alergias_ids=[a.id for a in perfil.alergias],
        ingredientes_evitados_ids=[
            i.id for i in perfil.ingredientes_evitados
        ],
        categorias_evitadas_ids=[
            c.id for c in perfil.categorias_evitadas
        ],
    )


@router.post(
    "",
    response_model=PerfilAlimentarioResponse,
    status_code=HTTPStatus.CREATED,
)
def crear_perfil(
    datos: PerfilAlimentarioCreate,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PerfilAlimentarioService(db)

    try:
        perfil = servicio.crear(cuenta_actual.id, datos)

    except PerfilYaExisteError as error:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(error),
        ) from error

    except CatalogoInvalidoError as error:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return preparar_respuesta(perfil)


@router.get(
    "/me",
    response_model=PerfilAlimentarioResponse,
    status_code=HTTPStatus.OK,
)
def obtener_mi_perfil(
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PerfilAlimentarioService(db)

    try:
        perfil = servicio.obtener(cuenta_actual.id)

    except PerfilNoEncontradoError as error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=str(error),
        ) from error

    return preparar_respuesta(perfil)


@router.put(
    "/me",
    response_model=PerfilAlimentarioResponse,
    status_code=HTTPStatus.OK,
)
def actualizar_mi_perfil(
    datos: PerfilAlimentarioCreate,
    cuenta_actual: Cuenta = Depends(obtener_cuenta_actual),
    db: Session = Depends(get_db),
):
    servicio = PerfilAlimentarioService(db)

    try:
        perfil = servicio.actualizar(cuenta_actual.id, datos)

    except PerfilNoEncontradoError as error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=str(error),
        ) from error

    except CatalogoInvalidoError as error:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return preparar_respuesta(perfil)
