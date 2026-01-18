from pydantic_settings import BaseSettings
from pydantic import computed_field
import pathlib

current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
env_file_path = project_root / ".env"

class Settings(BaseSettings):
    MONGO_APP_USER: str
    MONGO_APP_PASS: str
    MONGO_AUTH_SOURCE: str
    MONGO_HOST: str = "mongo"
    MONGO_PORT: int = 27017

    SERVICE_USERNAME: str
    SERVICE_PASSWORD: str

    EVENIMENTE_SERVICE_URL: str

    @computed_field
    @property
    def MONGO_DATABASE_URL(self) -> str:
        return (
            f"mongodb://{self.MONGO_APP_USER}:{self.MONGO_APP_PASS}@"
            f"{self.MONGO_HOST}:{self.MONGO_PORT}/"
            f"?authSource={self.MONGO_AUTH_SOURCE}"
        )

    class Config:
        env_file = env_file_path
        env_file_encoding = "utf-8"
        extra = "ignore"

config = Settings()