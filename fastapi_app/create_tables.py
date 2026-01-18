import asyncio
from fastapi_app.core.database import sessionmanager, Base
from fastapi_app.models import Eveniment, Bilet, JoinPE, Pachet

async def main():
    async with sessionmanager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tabele create cu succes!")

if __name__ == "__main__":
    asyncio.run(main())