import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

from fastapi_app.core.database import Base

ADMIN_DB_HOST = os.getenv("DB_HOST", "mariadb-event")
ADMIN_DB_PORT = "3306"

ADMIN_DB_USER = "root"
ADMIN_DB_PASS = os.getenv("ROOT_DB_PASS")
ADMIN_DB_NAME = os.getenv("DB_NAME")

APP_DB_USER = os.getenv("DB_USER")
APP_DB_PASS = os.getenv("DB_PASS")

if not ADMIN_DB_PASS:
    raise ValueError("ROOT_DB_PASS nu este setat. Verifică secțiunea environment din compose!")
if not all([APP_DB_USER, APP_DB_PASS, ADMIN_DB_NAME]):
    raise ValueError("Variabilele pentru utilizatorul aplicației lipsesc din environment.")

DATABASE_URL_ADMIN = (
    f"mysql+aiomysql://"
    f"{ADMIN_DB_USER}:{ADMIN_DB_PASS}@"
    f"{ADMIN_DB_HOST}:{ADMIN_DB_PORT}/{ADMIN_DB_NAME}"
)

engine = create_async_engine(DATABASE_URL_ADMIN, echo=True)


async def create_db_and_user():
    max_tries = 15
    count = 0
    print(f"Încercare conectare la {ADMIN_DB_HOST}:{ADMIN_DB_PORT}...")

    while count < max_tries:
        try:
            async with engine.begin() as conn:
                print(f"Crearea/Verificarea utilizatorului '{APP_DB_USER}'...")
                await conn.execute(
                    text(f"CREATE USER IF NOT EXISTS '{APP_DB_USER}'@'%' IDENTIFIED BY '{APP_DB_PASS}'")
                )

                print(f"Acordarea privilegiilor pe baza '{ADMIN_DB_NAME}'...")
                await conn.execute(
                    text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON `{ADMIN_DB_NAME}`.* TO '{APP_DB_USER}'@'%'")
                )

                await conn.execute(text("FLUSH PRIVILEGES;"))

                print("Stergere și recreare tabele prin Base.metadata...")
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            print("Succes: Utilizatorul și tabelele au fost create!")
            break

        except OperationalError as e:
            count += 1
            print(f"Baza de date nu este gata încă (Încercarea {count}/{max_tries}). Reîncercare în 2s...")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Eroare neașteptată: {e}")
            break

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_db_and_user())