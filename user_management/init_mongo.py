import os
from pymongo import MongoClient

MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = "27017"
ROOT_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
ROOT_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "example")

APP_DB = "user_management"
COLLECTION_NAME = "clienti"

root_uri = f"mongodb://{ROOT_USER}:{ROOT_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
client = MongoClient(root_uri)


def initialize_database():
    try:
        db = client[APP_DB]

        try:
            db.command("createUser", os.getenv("MONGO_APP_USER", "user_rw"),
                       pwd=os.getenv("MONGO_APP_PASS", "password"),
                       roles=[{"role": "readWrite", "db": APP_DB}, {"role": "dbOwner", "db": APP_DB}])
            print("Utilizator de sistem creat.")
        except Exception:
            print("Utilizatorul de sistem exista deja.")


        clienti_collection = db[COLLECTION_NAME]

        test_client = {
            "nume": "Doe",
            "prenume": "John",
            "email": "client@client.com",
            "lista_bilete": []
        }

        result = clienti_collection.update_one(
            {"email": test_client["email"]},
            {"$setOnInsert": test_client},
            upsert=True
        )

        if result.upserted_id:
            print(f"Succes: Profilul pentru {test_client['email']} a fost creat în MongoDB.")
        else:
            print(f"Notă: Profilul pentru {test_client['email']} exista deja în MongoDB.")

    except Exception as e:
        print(f"Eroare: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    initialize_database()