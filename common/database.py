import os
import pymongo

# database connection setup
mongo_string = f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@discordbotcluster.afgyl.mongodb.net/GumbotchiDB?retryWrites=true&w=majority"
db = pymongo.MongoClient(mongo_string).GumbotchiDB

guilds = db.Guilds
users = db.Users

print("Connected to Database.")

user = {
    "_id": 123,
    "zipcode": 21758,
    "site": "washingtondc",
    "clqueries": [
        {
            "max_price": 123.23,
            "distance": 50,
            "has_image": True,
            "keyword": ["abc", "cde"],
            "sent_listings": [123, 124],
            "channel": 123
        }
    ]
}


#  site, max_price, zip_code, distance, has_image, keywords, sent_listings)

def guildget(gid, field):
    """Fetches and unpacks one field from the database."""
    data = guilds.find_one({"_id": gid}, {field: 1, "_id": 0})
    if not data:
        data = {
            "_id": gid,
            "prefix": "!",
            "groups": []
        }
        guilds.insert_one(data)
    return data[field]


def guildget_many(gid, *fields):
    """Fetches and unpacks many field from the database."""
    projection = {field: 1 for field in fields}
    projection.update({"_id": 0})

    data = guilds.find_one({"_id": gid}, projection)
    if not data:
        data = {
            "_id": gid,
            "prefix": "!",
            "groups": []
        }
        guilds.insert_one(data)
    return data.values()


def userget(uid, field):
    """Fetches and unpacks one field from the database."""
    data = users.find_one({"_id": uid}, {field: 1, "_id": 0})
    if not data:
        data = {
            "_id": uid,
            "zipcode": None,
            "site": None,
            "clqueries": []
        }
        users.insert_one(data)
    return data[field]


def userget_many(uid, *fields):
    """Fetches and unpacks many field from the database."""
    projection = {field: 1 for field in fields}
    projection.update({"_id": 0})

    data = users.find_one({"_id": uid}, projection)
    if not data:
        data = {
            "_id": uid,
            "zipcode": None,
            "site": None,
            "clqueries": []
        }
        users.insert_one(data)
    return data.values()
