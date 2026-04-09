from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hospital Appointment SaaS"
    environment: str = "dev"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/hospital_saas"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    # Optional integration settings
    whatsapp_access_token: str | None = None
    whatsapp_phone_number_id: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
