from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
FILES_DIR = DATA_DIR / "files"
DB_PATH = DATA_DIR / "workorders.sqlite"


class Settings(BaseSettings):
    portal_api_url: str = "https://api-imasm.insytedeutschland.de"
    username: str = ""
    password: str = ""
    ssl_verify: bool = False
    request_timeout: float = 30.0
    request_retries: int = 3

    class Config:
        env_file = BASE_DIR / ".env"


settings = Settings()
