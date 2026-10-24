
from abc import ABC, abstractmethod

from app.models.receta import Receta
from app.models.perfil_alimentario import PerfilAlimentario


class RestriccionStrategy(ABC):
    """Interfaz común para evaluar restricciones alimentarias."""

    @abstractmethod
    def es_compatible(
        self,
        receta: Receta,
        perfil: PerfilAlimentario,
    ) -> bool:
        """Indica si una receta cumple una restricción alimentaria."""
        pass
