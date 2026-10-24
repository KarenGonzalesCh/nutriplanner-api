
from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario
from app.strategies.restriccion import RestriccionStrategy


class RestriccionIngredientesStrategy(RestriccionStrategy):
    """Verifica que la receta no contenga ingredientes evitados."""

    def es_compatible(
        self,
        receta: Receta,
        perfil: PerfilAlimentario,
    ) -> bool:

        ingredientes_evitados = {
            ingrediente.id
            for ingrediente in perfil.ingredientes_evitados
        }

        for receta_ingrediente in receta.ingredientes:
            ingrediente = receta_ingrediente.ingrediente

            if ingrediente.id in ingredientes_evitados:
                return False

        return True
