import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from auth_service.auth import hash_password
from auth_service.models.idm_models import Base, User, UserRole

DB_HOST = os.getenv("IDM_DB_HOST", "mariadb-idm")
DB_PORT = "3306"
DB_USER = "root"
DB_PASS = os.getenv("IDM_ROOT_PASS", "root_pass_idm")
DB_NAME = "idm_database"

IDM_DB_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(IDM_DB_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)
async def init_idm():
    async with engine.begin() as conn:
        print(f"Conectat la: {DB_HOST}:{DB_PORT}. Stergere și recreare tabele...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            print("Inserare utilizatori prin ORM")
            users = [
                User(
                    username="admin@admin.com",
                    password=hash_password("admin123"),
                    role=UserRole.ADMIN
                ),
                User(
                    username="owner@owner.com",
                    password=hash_password("owner123"),
                    role=UserRole.OWNER_EVENT
                ),
                User(
                    username="client@client.com",
                    password=hash_password("client123"),
                    role=UserRole.CLIENT
                ),
                User(
                    username="serviciu@serviciu.com",
                    password=hash_password("serviciu123"),
                    role=UserRole.SERVICE_CLIENTI
                )
            ]
            session.add_all(users)
    print("IDM BD init success")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_idm())