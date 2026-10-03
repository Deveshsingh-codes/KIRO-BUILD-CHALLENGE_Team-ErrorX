from pymongo import MongoClient
from pymongo.database import Database
from app.config.settings import settings

client: MongoClient = None
db: Database = None

def connect_to_mongo():
    global client, db
    client = MongoClient(settings.mongodb_uri)
    db = client.get_database()
    print("✓ Connected to MongoDB")

def close_mongo_connection():
    global client
    if client:
        client.close()
        print("✓ Closed MongoDB connection")

def get_database() -> Database:
    return db
