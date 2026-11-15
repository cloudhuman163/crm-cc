from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # telefony: mock | ami
    telefony: str = "mock"
    # billing: mock | http
    billing_mode: str = "mock"

    database_url: str = "postgresql+asyncpg://crm:crm@db:5432/crm_cc"
    redis_url: str = "redis://redis:6379/0"

    ami_host: str = ""
    ami_port: int = 5038
    ami_user: str = ""
    ami_pass: str = ""

    billing_url: str = ""
    billing_token: str = ""

    app_token: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
