from pymongo import AsyncMongoClient
from .config import config

uri = config.MONGO_DATABASE_URL

client = AsyncMongoClient(uri)
db = client.get_database("user_management")
client_collection = db.get_collection("clienti")
