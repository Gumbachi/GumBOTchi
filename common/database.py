import os

import pymongo

# database connection setup
mongo_string = f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@discordbotcluster.afgyl.mongodb.net/GumbotchiDB?retryWrites=true&w=majority"
connection = pymongo.MongoClient(mongo_string)


class DB:

    def __init__(self, connection: pymongo.MongoClient):
        self._db = connection.GumbotchiDB
        self._guilds = self._db.Guilds
        self._users = self._db.Users
        self._queries = self._db.Queries

    @staticmethod
    def default_guild(id: int):
        return {
            "_id": id,
            "pogresponses": [],
            "iexkey": None,
        }

    @staticmethod
    def default_user(id: int):
        return {
            "_id": id,
            "query_ids": []
        }

    def insert_guild(self, id: int):
        """Insert a guild for the id provided and return the empty guild"""
        empty_guild = self.default_guild(id=id)
        self._guilds.insert_one(empty_guild)
        return empty_guild

    def insert_user(self, id: int):
        """Insert a user for the id provided and return the empty user"""
        blank_user = self.default_user(id=id)
        self._users.insert_one(blank_user)
        return blank_user

    def get_guild(self, id: int) -> dict:
        """Fetch the guild document or add one if not exists."""
        data = self._guilds.find_one({"_id": id})
        return data or self.insert_guild(id=id)

    def get_user(self, id: int) -> dict:
        """Fetch the user document or add one if not exists."""
        data = self._users.find_one({"_id": id})
        return data or self.insert_user(id=id)

    def add_pog_response(self, id: int, pogresponse: str):
        """Add a pog response to the db."""
        response = self._guilds.update_one(
            filter={"_id": id},
            update={"$push": {"pogresponses": pogresponse}},
            upsert=True
        )

        return response.modified_count != 0

    def remove_pog_response(self, id: int, pogresponse: str):
        """Remove a pog response from the db."""
        response = self._guilds.update_one(
            filter={"_id": id},
            update={"$pull": {"pogresponses": pogresponse}}
        )

        return response.modified_count != 0

    def get_pogresponses(self, id: int) -> list[str]:
        """Retrieve the list of pog responses."""
        response = self._guilds.find_one(
            filter={"_id": id},
            projection={"_id": 0, "pogresponses": 1}
        )

        if not response:
            response = self.insert_guild(id=id)

        return response.get("pogresponses") or []

    def set_sbonk_key(self, id: int, key: str):
        """Retrieve the publishable API key set for the guild."""
        response = self._guilds.update_one(
            filter={"_id": id},
            update={"$set": {"iexkey": key}},
            upsert=True
        )

        return response.modified_count != 0

    def get_sbonk_key(self, id: int) -> str | None:
        """Retrieve the publishable API key set for the guild."""
        response = self._guilds.find_one(
            filter={"_id": id},
            projection={"_id": 0, "iexkey": 1}
        )

        if not response:
            response = self.insert_guild(id=id)

        return response.get("iexkey")

    def insert_query(self, query):
        response = self._queries.insert_one(query.to_db())
        return response.acknowledged

    def delete_query(self, query):
        response = self._queries.delete_one(query.to_db())
        return response.acknowledged

    def get_queries(self):
        return self._queries.find({})


db = DB(connection)
print("Connected to DB")
