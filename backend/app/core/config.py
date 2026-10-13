
import re

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0, le=1440)
    OTP_SECRET: SecretStr

    RESEND_API_KEY: SecretStr
    EMAIL_FROM: str

    ENVIRONMENT: str = "development"
    SQL_ECHO: bool = False
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("Only HS256 is permitted for JWT signing")
        return value

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"development", "testing", "production"}:
            raise ValueError("ENVIRONMENT must be development, testing, or production")
        return value

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins:
            raise ValueError("At least one CORS origin must be configured")
        if any(origin == "*" for origin in origins):
            raise ValueError("Wildcard CORS origins are not permitted")
        return ",".join(origins)

    @model_validator(mode="after")
    def validate_security_settings(self):
        secret = self.SECRET_KEY.get_secret_value()
        otp_secret = self.OTP_SECRET.get_secret_value()

        if len(secret) < 32:
            raise ValueError("SECRET_KEY must contain at least 32 characters")

        if len(otp_secret) < 32:
            raise ValueError("OTP_SECRET must contain at least 32 characters")

        if secret == otp_secret:
            raise ValueError("SECRET_KEY and OTP_SECRET must be different")

        if self.ENVIRONMENT == "production":
            if self.SQL_ECHO:
                raise ValueError("SQL_ECHO must be disabled in production")

            if any(
                not origin.startswith("https://")
                for origin in self.cors_origins
            ):
                raise ValueError("Production CORS origins must use HTTPS")

        return self

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()