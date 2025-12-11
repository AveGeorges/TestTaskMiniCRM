from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    DATABASE_URL: str
    APP_NAME: str
    APP_DESCRIPTION: str
    APP_VERSION: str
    DEBUG: bool = False
    API_V1_PREFIX: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
