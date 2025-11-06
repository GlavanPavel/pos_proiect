import asyncio
import os
import time
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

from fastapi_app.core.database import Base
from fastapi_app.models.eveniment import Eveniment
from fastapi_app.models.pachet import Pachet
from fastapi_app.models.bilet import Bilet
from fastapi_app.models.join_pe import JoinPE

load_dotenv(".env")

ADMIN_DB_USER = "root"
ADMIN_DB_PASS = os.getenv("ROOT_DB_PASS")
ADMIN_DB_HOST = os.getenv("DB_HOST", "localhost")
ADMIN_DB_PORT = os.getenv("DB_PORT", "3306")
ADMIN_DB_NAME = os.getenv("DB_NAME")

APP_DB_USER = os.getenv("DB_USER")
APP_DB_PASS = os.getenv("DB_PASS")

if not ADMIN_DB_PASS:
    raise ValueError("ROOT_DB_PASS nu este setat în fisierul .env")
if not all([APP_DB_USER, APP_DB_PASS, ADMIN_DB_NAME]):
    raise ValueError(".env incomplet")

DATABASE_URL_ADMIN = (
    f"mysql+aiomysql://"
    f"{ADMIN_DB_USER}:{ADMIN_DB_PASS}@"
    f"{ADMIN_DB_HOST}:{ADMIN_DB_PORT}/{ADMIN_DB_NAME}"
)

engine = create_async_engine(DATABASE_URL_ADMIN)


async def create_db_and_user():
    max_tries = 15
    count = 0

    while count < max_tries:
        try:
            async with engine.begin() as conn:

                print(f"Crearea utilizatorului '{APP_DB_USER}'...")
                await conn.execute(text(f"CREATE USER IF NOT EXISTS :user@'%' IDENTIFIED BY :pass"),
                                   {"user": APP_DB_USER, "pass": APP_DB_PASS})

                print(f"Acordarea privilegiilor pentru '{APP_DB_USER}'...")

                await conn.execute(text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON `{ADMIN_DB_NAME}`.* TO :user@'%'"),
                                   {"user": APP_DB_USER})

                await conn.execute(text("FLUSH PRIVILEGES;"))
                await conn.run_sync(Base.metadata.drop_all, checkfirst=True)

                print("Crearea tabelelor noi")
                await conn.run_sync(Base.metadata.create_all)

            break

        except OperationalError as e:
            count += 1
            if count >= max_tries:
                print("Eroare: S-a depasit numarul maxim de incercari.")
                raise
            await asyncio.sleep(2)

    print("Utilizatorul și tabelele au fost create cu succes.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_db_and_user())