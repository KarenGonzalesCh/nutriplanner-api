from dataclasses import dataclass
from app.core.enums import NivelDificultad, TipoComida
from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario
from heapq import heappop, heappush


# RN3: correspondencia entre nivel del usuario
# y dificultad permitida para sugerencias automáticas.
NIVELES_PERMITIDOS = {
    NivelDificultad.PRINCIPIANTE: {
        NivelDificultad.PRINCIPIANTE,
    },
    NivelDificultad.INTERMEDIO: {
        NivelDificultad.PRINCIPIANTE,
        NivelDificultad.INTERMEDIO,
    },
    NivelDificultad.AVANZADO: {
        NivelDificultad.PRINCIPIANTE,
        NivelDificultad.INTERMEDIO,
        NivelDificultad.AVANZADO,
    },
}


def filtrar_candidatas_basicas(
    recetas: list[Receta],
    perfil: PerfilAlimentario,
    tipo_comida: TipoComida,
) -> list[Receta]:
    """
    Filtra recetas activas por tipo de comida y nivel culinario.

    Este filtro NO evalúa todavía restricciones alimentarias,
    exclusiones personales ni reportes pendientes.
    """

    niveles_permitidos = NIVELES_PERMITIDOS[
        perfil.nivel_culinario
    ]

    candidatas = []

    for receta in recetas:

        if not receta.activa:
            continue

        if receta.dificultad not in niveles_permitidos:
            continue

        tipos_receta = {
            relacion.tipo_comida
            for relacion in receta.tipos_comida
        }

        if tipo_comida not in tipos_receta:
            continue

        candidatas.append(receta)

    return candidatas

@dataclass(frozen=True)
class CandidataMenu:
    receta_id: int
    tiene_conflicto_flexible: bool


def seleccionar_candidata(
    candidatas: list[CandidataMenu],
    recetas_utilizadas: set[int],
) -> CandidataMenu | None:
    """
    Selecciona una receta aplicando RN28.

    Se presupone que las candidatas ya fueron filtradas
    por tipo de comida, dificultad, restricciones
    obligatorias, exclusiones y reportes pendientes.

    No realiza sustituciones automáticamente.
    """

    if not candidatas:
        return None

    def prioridad(candidata: CandidataMenu):
        repetida = candidata.receta_id in recetas_utilizadas

        return (
            repetida,
            candidata.tiene_conflicto_flexible,
            candidata.receta_id,
        )

    return min(candidatas, key=prioridad)

@dataclass(frozen=True)
class ComidaPropuesta:
    dia: int
    tipo_comida: TipoComida
    receta_id: int | None
    tiene_conflicto_flexible: bool = False


@dataclass(frozen=True)
class PropuestaMenu:
    comidas: list[ComidaPropuesta]

    @property
    def completa(self) -> bool:
        return all(
            comida.receta_id is not None
            for comida in self.comidas
        )



def _asignar_distintas_optimas(
    opciones: list[list[CandidataMenu]],
) -> dict[int, CandidataMenu]:
    """
    Obtiene una asignación de recetas sin repeticiones.

    Objetivos, en orden:
    1. Maximizar la cantidad de espacios con recetas distintas.
    2. Minimizar los conflictos flexibles entre esas asignaciones.

    Utiliza un grafo de flujo de costo mínimo.
    """

    # Si un ID aparece más de una vez en una posición,
    # conservar su versión con menos conflictos.
    normalizadas = []

    for grupo in opciones:
        por_id = {}

        for candidata in grupo:
            anterior = por_id.get(candidata.receta_id)

            if (
                anterior is None
                or (
                    anterior.tiene_conflicto_flexible
                    and not candidata.tiene_conflicto_flexible
                )
            ):
                por_id[candidata.receta_id] = candidata

        normalizadas.append(por_id)

    ids_recetas = sorted({
        receta_id
        for grupo in normalizadas
        for receta_id in grupo
    })

    indices_recetas = {
        receta_id: indice
        for indice, receta_id in enumerate(ids_recetas)
    }

    # Nodos del grafo:
    # fuente -> espacios del menú -> recetas -> sumidero
    fuente = 0
    primer_espacio = 1
    primera_receta = primer_espacio + len(opciones)
    sumidero = primera_receta + len(ids_recetas)

    grafo = [[] for _ in range(sumidero + 1)]

    def conectar(origen: int, destino: int, costo: int):
        # Arista: [destino, capacidad, costo, índice inverso]
        directa = [
            destino,
            1,
            costo,
            len(grafo[destino]),
        ]

        inversa = [
            origen,
            0,
            -costo,
            len(grafo[origen]),
        ]

        grafo[origen].append(directa)
        grafo[destino].append(inversa)

    # Cada espacio puede recibir una única receta.
    for posicion in range(len(opciones)):
        conectar(fuente, primer_espacio + posicion, 0)

    # Una receta sin conflicto tiene costo 0.
    # Una receta con conflicto flexible tiene costo 1.
    for posicion, grupo in enumerate(normalizadas):
        for receta_id in sorted(grupo):
            candidata = grupo[receta_id]

            conectar(
                primer_espacio + posicion,
                primera_receta + indices_recetas[receta_id],
                int(candidata.tiene_conflicto_flexible),
            )

    # En esta fase, cada receta puede utilizarse una vez.
    for indice in range(len(ids_recetas)):
        conectar(primera_receta + indice, sumidero, 0)

    infinito = float("inf")
    potenciales = [0] * len(grafo)

    # Buscar caminos de menor costo y aumentar
    # la cantidad de asignaciones mientras sea posible.
    while True:
        distancias = [infinito] * len(grafo)
        anteriores = [None] * len(grafo)

        distancias[fuente] = 0
        cola = [(0, fuente)]

        while cola:
            distancia, origen = heappop(cola)

            if distancia != distancias[origen]:
                continue

            for indice, arista in enumerate(grafo[origen]):
                destino, capacidad, costo, _ = arista

                if capacidad == 0:
                    continue

                costo_ajustado = (
                    costo
                    + potenciales[origen]
                    - potenciales[destino]
                )

                nueva_distancia = (
                    distancia + costo_ajustado
                )

                if nueva_distancia < distancias[destino]:
                    distancias[destino] = nueva_distancia
                    anteriores[destino] = (origen, indice)

                    heappush(
                        cola,
                        (nueva_distancia, destino),
                    )

        # No quedan más asignaciones distintas posibles.
        if anteriores[sumidero] is None:
            break

        for nodo, distancia in enumerate(distancias):
            if distancia != infinito:
                potenciales[nodo] += distancia

        # Actualizar las capacidades del camino elegido.
        actual = sumidero

        while actual != fuente:
            origen, indice = anteriores[actual]
            arista = grafo[origen][indice]

            arista[1] -= 1
            grafo[actual][arista[3]][1] += 1

            actual = origen

    # Reconstruir la asignación obtenida.
    asignadas = {}

    for posicion, grupo in enumerate(normalizadas):
        nodo = primer_espacio + posicion

        for arista in grafo[nodo]:
            destino, capacidad, _, _ = arista

            if (
                primera_receta <= destino < sumidero
                and capacidad == 0
            ):
                receta_id = ids_recetas[
                    destino - primera_receta
                ]

                asignadas[posicion] = grupo[receta_id]
                break

    return asignadas


def armar_propuesta_menu(
    cantidad_dias: int,
    tipos_comida: list[TipoComida],
    candidatas_por_tipo: dict[
        TipoComida,
        list[CandidataMenu],
    ],
) -> PropuestaMenu:
    """
    Construye una propuesta temporal de 1 a 7 días.

    Las candidatas deben haber superado previamente
    todas las validaciones de elegibilidad obligatoria.

    No guarda menús ni sustituye ingredientes.
    """

    if not 1 <= cantidad_dias <= 7:
        raise ValueError(
            "El menú debe tener entre 1 y 7 días"
        )

    if not tipos_comida:
        raise ValueError(
            "Debe seleccionarse al menos una comida"
        )

    if len(tipos_comida) != len(set(tipos_comida)):
        raise ValueError(
            "No se pueden repetir tipos de comida por día"
        )

    espacios = [
        (dia, tipo)
        for dia in range(1, cantidad_dias + 1)
        for tipo in tipos_comida
    ]

    opciones = [
        candidatas_por_tipo.get(tipo, [])
        for _, tipo in espacios
    ]

    # Buscar la máxima variedad con el mínimo
    # número posible de conflictos flexibles.
    asignadas = _asignar_distintas_optimas(opciones)

    utilizadas = {
        candidata.receta_id
        for candidata in asignadas.values()
    }

    # Solo repetir cuando ya no sea posible
    # asignar más recetas diferentes.
    for posicion in range(len(espacios)):
        if posicion in asignadas:
            continue

        candidata = seleccionar_candidata(
            opciones[posicion],
            utilizadas,
        )

        if candidata is not None:
            asignadas[posicion] = candidata
            utilizadas.add(candidata.receta_id)

    comidas = []

    for posicion, (dia, tipo) in enumerate(espacios):
        candidata = asignadas.get(posicion)

        comidas.append(
            ComidaPropuesta(
                dia=dia,
                tipo_comida=tipo,
                receta_id=(
                    candidata.receta_id
                    if candidata is not None
                    else None
                ),
                tiene_conflicto_flexible=(
                    candidata.tiene_conflicto_flexible
                    if candidata is not None
                    else False
                ),
            )
        )

    return PropuestaMenu(comidas=comidas)


def _completar_con_distintas(
    opciones: list[list[CandidataMenu]],
    asignadas: dict[int, CandidataMenu],
) -> dict[int, CandidataMenu]:
    """
    Completa los espacios pendientes con recetas distintas.

    Puede reorganizar asignaciones previas para evitar
    repeticiones, incluso usando candidatas con
    conflictos flexibles.
    """

    propietarios = {
        candidata.receta_id: posicion
        for posicion, candidata in asignadas.items()
    }

    def buscar_reasignacion(
        posicion: int,
        visitadas: set[int],
    ) -> bool:

        candidatas_ordenadas = sorted(
            opciones[posicion],
            key=lambda c: c.tiene_conflicto_flexible,
        )

        for candidata in candidatas_ordenadas:
            receta_id = candidata.receta_id

            if receta_id in visitadas:
                continue

            visitadas.add(receta_id)

            propietario = propietarios.get(receta_id)

            if (
                propietario is None
                or buscar_reasignacion(propietario, visitadas)
            ):
                propietarios[receta_id] = posicion
                return True

        return False

    pendientes = [
        posicion
        for posicion in range(len(opciones))
        if posicion not in asignadas
    ]

    for posicion in sorted(
        pendientes,
        key=lambda i: len(opciones[i]),
    ):
        buscar_reasignacion(posicion, set())

    return {
        posicion: next(
            candidata
            for candidata in opciones[posicion]
            if candidata.receta_id == receta_id
        )
        for receta_id, posicion in propietarios.items()
    }
