
from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario
from app.strategies.restriccion import RestriccionStrategy
from app.strategies.restriccion_alergias import RestriccionAlergiasStrategy
from app.strategies.restriccion_ingredientes import RestriccionIngredientesStrategy
from app.strategies.restriccion_categorias import RestriccionCategoriasStrategy

class EvaluadorRestricciones:
    """Evalúa una receta utilizando las estrategias configuradas."""

    def __init__(
        self,
        estrategias: list[RestriccionStrategy],
    ):
        self.estrategias = estrategias

    def es_compatible(
        self,
        receta: Receta,
        perfil: PerfilAlimentario,
    ) -> bool:
        return all(
            estrategia.es_compatible(receta, perfil)
            for estrategia in self.estrategias
        )



def crear_evaluador_restricciones() -> EvaluadorRestricciones:
    """Crea un evaluador con las restricciones alimentarias del perfil."""

    estrategias = [
        RestriccionAlergiasStrategy(),
        RestriccionIngredientesStrategy(),
        RestriccionCategoriasStrategy(),
    ]

    return EvaluadorRestricciones(estrategias)
