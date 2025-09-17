from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List, Union

class Settings(BaseSettings):
    APP_NAME: str = "Finance Manager"
    APP_ENV: str = "development"
    SECRET_KEY: str = "CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    DATABASE_URL: str = "sqlite:///./app.db"
    CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = "*"

    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "ChangeMe123!"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

settings = Settings()  # type: ignore
