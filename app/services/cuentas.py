from sqlalchemy.orm import Session

from app.core.enums import Rol
from app.core.security import generar_hash, verificar_password
from app.models.cuenta import Cuenta
from app.repositories.cuenta import CuentaRepository
from app.schemas.cuenta import CuentaCreate


class CuentaYaExisteError(Exception):
    """Indica que el correo o nombre de usuario ya está registrado."""





class CredencialesInvalidasError(Exception):
    """Indica que el usuario o la contraseña son incorrectos."""


class CuentaService:

    def __init__(self, db: Session):
        self.repository = CuentaRepository(db)

    def registrar(self, datos: CuentaCreate) -> Cuenta:
        if self.repository.obtener_por_correo(datos.correo):
            raise CuentaYaExisteError("El correo ya está registrado")

        if self.repository.obtener_por_nombre_usuario(
            datos.nombre_usuario
        ):
            raise CuentaYaExisteError(
                "El nombre de usuario ya está registrado"
            )

        nueva_cuenta = Cuenta(
            nombre_usuario=datos.nombre_usuario,
            correo=datos.correo,
            password_hash=generar_hash(datos.password),
            rol=Rol.USUARIO,
        )

        return self.repository.crear(nueva_cuenta)

    
    def autenticar(self, correo: str, password: str) -> Cuenta:
        cuenta = self.repository.obtener_por_correo(correo)

        if cuenta is None:
            raise CredencialesInvalidasError(
                "Credenciales incorrectas"
            )

        if not verificar_password(password, cuenta.password_hash):
            raise CredencialesInvalidasError(
                "Credenciales incorrectas"
            )

        return cuenta
