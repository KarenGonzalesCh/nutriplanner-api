
from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario
from app.strategies.restriccion import RestriccionStrategy


class RestriccionCategoriasStrategy(RestriccionStrategy):
    """Verifica que la receta no contenga categorías evitadas."""

    def es_compatible(
        self,
        receta: Receta,
        perfil: PerfilAlimentario,
    ) -> bool:

        categorias_evitadas = {
            categoria.id
            for categoria in perfil.categorias_evitadas
        }

        for receta_ingrediente in receta.ingredientes:
            ingrediente = receta_ingrediente.ingrediente

            if ingrediente.categoria_id in categorias_evitadas:
                return False

        return True
