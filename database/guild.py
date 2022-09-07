import os
from typing import Any

import pymongo

# database connection setup
mongo_string = f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@discordbotcluster.afgyl.mongodb.net/GumbotchiDB?retryWrites=true&w=majority"
connection = pymongo.MongoClient(mongo_string)
db = connection.GumbotchiDB

print("Connected to DB")


def generate_default_guild(id: int) -> dict[str, Any]:
    return {"_id": id, "iexkey": None, "pogactivators": [], "pogresponses": []}


def insert_guild(id: int) -> dict[str, Any]:
    """Insert a guild for the id provided and return the empty guild."""
    empty_guild = generate_default_guild(id=id)
    db.Guilds.insert_one(empty_guild)
    return empty_guild


def get_guild(id: int) -> dict:
    """Fetch the guild document or add one if not exists."""
    data = db.Guilds.find_one({"_id": id})

    # return found data or a default guild
    return data if data is not None else insert_guild(id=id)
