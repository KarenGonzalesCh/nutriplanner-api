
from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario
from app.strategies.restriccion import RestriccionStrategy


class RestriccionAlergiasStrategy(RestriccionStrategy):
    """Verifica que una receta no contenga alérgenos del perfil."""

    def es_compatible(
        self,
        receta: Receta,
        perfil: PerfilAlimentario,
    ) -> bool:

        alergias_usuario = {
            alergia.id for alergia in perfil.alergias
        }

        for receta_ingrediente in receta.ingredientes:
            ingrediente = receta_ingrediente.ingrediente

            for alergia in ingrediente.alergias:
                if alergia.id in alergias_usuario:
                    return False

        return True
