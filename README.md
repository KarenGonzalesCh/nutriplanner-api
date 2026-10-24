# NutriPlanner API

API REST de planificación alimentaria desarrollada como proyecto de **Programación 2 — UNSAM**.

NutriPlanner tiene como objetivo permitir a los usuarios generar menús personalizados para períodos de entre 1 y 7 días, considerando sus alergias, alimentos a evitar, preferencias alimentarias y nivel culinario.

El proyecto está desarrollado en **Python**, utilizando FastAPI, SQLAlchemy y una arquitectura organizada en capas.

## Estado del desarrollo

### Funcionalidades implementadas

- Modelos de datos para cuentas, perfiles alimentarios, alergias, ingredientes, categorías de alimentos y recetas.
- Registro de usuarios mediante `POST /cuentas`.
- Validación de datos de entrada mediante Pydantic.
- Almacenamiento seguro de contraseñas mediante Argon2.
- Inicio de sesión y autenticación mediante JWT.
- Consulta de la cuenta autenticada mediante `GET /cuentas/me`.
- Gestión de migraciones de base de datos mediante Alembic.
- Documentación interactiva de la API mediante Swagger.
- 28 pruebas automatizadas aprobadas.

### Funcionalidades pendientes

- Creación, consulta y modificación de perfiles alimentarios mediante endpoints.
- Evaluación de restricciones alimentarias mediante el patrón de diseño Strategy.
- Consulta y filtrado de recetas compatibles.
- Generación y administración de menús personalizados.
- Sustitución de recetas y revisión de compatibilidad.
- Funcionalidades de reportes y moderación.

## Tecnologías utilizadas

- **Python:** lenguaje de programación.
- **FastAPI:** desarrollo de la API REST.
- **SQLAlchemy:** mapeo objeto-relacional (ORM).
- **Pydantic:** validación de datos y schemas.
- **SQLite:** base de datos utilizada durante el desarrollo.
- **Alembic:** gestión de migraciones.
- **PyJWT:** generación y validación de tokens JWT.
- **pwdlib + Argon2:** hashing de contraseñas.
- **pytest:** pruebas automatizadas.
- **Uvicorn:** servidor de desarrollo.

## Estructura del proyecto

| Carpeta | Responsabilidad |
|---|---|
| `app/api/routes` | Endpoints de la API |
| `app/api/dependencies.py` | Dependencias de autenticación |
| `app/core` | Configuración, enums y seguridad |
| `app/db` | Conexión y sesiones de base de datos |
| `app/models` | Modelos SQLAlchemy |
| `app/schemas` | Schemas Pydantic de entrada y salida |
| `app/repositories` | Acceso a datos |
| `app/services` | Lógica de negocio |
| `alembic` | Migraciones de base de datos |
| `tests` | Pruebas automatizadas |
| `docs` | Documentación del proyecto |

## Puesta en marcha

### 1. Clonar el repositorio

```bash
git clone https://github.com/KarenGonzalesCh/nutriplanner-api.git
cd nutriplanner-api
```

### 2. Crear y activar el entorno virtual

En Linux o Ubuntu:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Nota para WSL:** si el proyecto está dentro de una carpeta de Windows montada en `/mnt/c`, puede ser conveniente crear el entorno virtual en el sistema de archivos de Ubuntu.

Por ejemplo:

```bash
mkdir -p ~/.virtualenvs
python3 -m venv ~/.virtualenvs/nutriplanner
source ~/.virtualenvs/nutriplanner/bin/activate
```

### 3. Instalar las dependencias

Con el entorno virtual activado:

```bash
python -m pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crear el archivo `.env` a partir de `.env.example`.

En Linux o Ubuntu:

```bash
cp .env.example .env
```

En Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

Configurar las variables correspondientes a la conexión de base de datos y la firma de los tokens JWT:

- `DATABASE_URL`: dirección de conexión a la base de datos.
- `SECRET_KEY`: clave secreta para firmar los tokens.

Opcionalmente:

- `ALGORITHM`: algoritmo JWT, por defecto `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: duración del token, por defecto 30 minutos.

**Importante:** el archivo `.env` contiene información sensible y no debe subirse a GitHub. Está excluido mediante `.gitignore`.

### 5. Crear las tablas de la base de datos

Ejecutar las migraciones mediante Alembic:

```bash
python -m alembic upgrade head
```

Este comando aplica las migraciones pendientes y prepara las tablas necesarias para utilizar la API.

### 6. Iniciar el servidor

```bash
python -m uvicorn app.main:app --reload
```

Una vez iniciado, la API estará disponible en:

http://127.0.0.1:8000

La documentación interactiva estará en:

http://127.0.0.1:8000/docs

También se puede consultar la documentación alternativa:

http://127.0.0.1:8000/redoc

## Endpoints implementados

| Método | Endpoint | Descripción | Autenticación |
|---|---|---|---|
| GET | `/health` | Verifica el funcionamiento de la API | No |
| POST | `/cuentas` | Registra una cuenta de usuario | No |
| POST | `/auth/token` | Autentica al usuario y genera un JWT | No |
| GET | `/cuentas/me` | Obtiene los datos de la cuenta autenticada | Sí |

### Registro de usuarios

**POST `/cuentas`**

Ejemplo de solicitud:

```json
{
  "nombre_usuario": "usuario_demo",
  "correo": "demo@example.com",
  "password": "ClaveDemo123"
}
```

Si el registro es exitoso, la API devuelve `201 Created`, con los datos de la cuenta sin incluir su contraseña ni el hash.

### Inicio de sesión

**POST `/auth/token`**

El endpoint recibe las credenciales mediante un formulario OAuth2:

- `username`: correo electrónico registrado.
- `password`: contraseña del usuario.

Si las credenciales son correctas, devuelve un token JWT con el formato:

```json
{
  "access_token": "<TOKEN_JWT>",
  "token_type": "bearer"
}
```

### Acceso a endpoints protegidos

Los endpoints protegidos requieren enviar el JWT en el encabezado HTTP:

```text
Authorization: Bearer <TOKEN_JWT>
```

También se puede utilizar el botón **Authorize** de Swagger para autenticarse y probar los endpoints protegidos.

## Pruebas automatizadas

El proyecto utiliza pytest para verificar el comportamiento de los modelos, el registro de cuentas, la autenticación y los endpoints HTTP.

Para ejecutar todas las pruebas:

```bash
python -m pytest -v
```

Hasta el momento se implementaron **28 pruebas automatizadas**, que cubren:

- Creación de tablas y relaciones entre modelos.
- Registro de cuentas.
- Validación de datos.
- Rechazo de usuarios duplicados.
- Hashing de contraseñas.
- Autenticación con credenciales válidas e inválidas.
- Generación y validación de JWT.
- Acceso a endpoints protegidos.
- Rechazo de tokens inválidos o vencidos.

Las pruebas de registro y autenticación utilizan una base SQLite temporal independiente de la base de datos de desarrollo.

## Migraciones de base de datos

Las migraciones se gestionan mediante Alembic.

Aplicar las migraciones pendientes:

```bash
python -m alembic upgrade head
```

Consultar la revisión actual:

```bash
python -m alembic current
```

Comprobar diferencias entre los modelos y la base de datos:

```bash
python -m alembic check
```

Cuando se modifiquen los modelos SQLAlchemy, se podrán generar nuevas migraciones mediante:

```bash
python -m alembic revision --autogenerate -m "descripcion del cambio"
```

Las migraciones generadas deben revisarse antes de aplicarlas.

## Docker

El repositorio incluye un `Dockerfile` para la containerización de la aplicación.

Construir la imagen:

```bash
docker build -t nutriplanner-api .
```

Ejecutar el contenedor:

```bash
docker run --env-file .env -p 8000:8000 nutriplanner-api
```

**Nota:** para ejecutar la aplicación en Docker es necesario que la base de datos configurada sea accesible desde el contenedor y que las migraciones estén aplicadas. La configuración completa de despliegue todavía requiere validación.

## Documentación

La documentación del proyecto se encuentra en la carpeta `docs`.

- Requerimientos: [docs/requirements.md](docs/requirements.md).

Los endpoints disponibles y sus schemas también pueden consultarse desde la documentación Swagger generada automáticamente por FastAPI.

## Próximas etapas

El desarrollo continuará con la implementación de los perfiles alimentarios, la evaluación de restricciones mediante el patrón Strategy y los servicios de generación de menús personalizados.