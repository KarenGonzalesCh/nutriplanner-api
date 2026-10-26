from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario
from app.strategies.restriccion import RestriccionStrategy
from app.services.compatibilidad_ingrediente import cumple_restriccion_alergias


class RestriccionAlergiasStrategy(RestriccionStrategy):
    """Verifica que una receta no contenga alérgenos del perfil."""

    def es_compatible(
        self,
        receta: Receta,
        perfil: PerfilAlimentario,
    ) -> bool:
        return all(
            cumple_restriccion_alergias(
                receta_ingrediente.ingrediente,
                perfil
            )
            for receta_ingrediente in receta.ingredientes
        )
