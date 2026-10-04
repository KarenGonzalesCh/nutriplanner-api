from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación, leída desde variables de entorno o .env.

    Los valores sensibles (database_url, secret_key) no tienen valor por defecto
    para que nunca queden escritos en el código fuente (RNF13).
    """

    app_name: str = "NutriPlanner API"
    app_version: str = "0.1.0"

    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
