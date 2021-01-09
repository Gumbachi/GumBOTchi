import os
import pymongo

# database connection setup
mongo_string = f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@discordbotcluster.afgyl.mongodb.net/GumbotchiDB?retryWrites=true&w=majority"
db = pymongo.MongoClient(mongo_string).GumbotchiDB
usercoll = db.UserData  # data for individual users
guildcoll = db.GuildData  # data for guilds
print("Connected to Database.")


def default_guild(id):
    """Generates a default document"""
    return {
        "_id": id,
        "prefix": "!",
    }


def default_member(id):
    """Default member document."""
    return {
        "_id": id,
        "watchlist": []
    }


def update_guild(id, data):
    """Updates guild data in a cleaner format than mongodb query."""
    return guildcoll.update_one({"_id": id}, {"$set": data}, upsert=True)


def update_user(id, data):
    return usercoll.update_one({"_id": id}, {"$set": data}, upsert=True)


def add_blank_guild(id):
    """Adds a blank guild"""
    update_guild(id, default_guild(id))  # adds or updates existing doc
