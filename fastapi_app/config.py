import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    DATABASE_URL: str = os.getenv(
        "DB_CONFIG",
        "mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}".format(
            DB_USER=os.getenv("DB_USERNAME"),
            DB_PASSWORD=os.getenv("DB_PASSWORD"),
            DB_HOST=os.getenv("DB_HOST"),
            DB_PORT=os.getenv("DB_PORT"),
            DB_NAME=os.getenv("DB_NAME"),
        ),
    )

config = Config()
