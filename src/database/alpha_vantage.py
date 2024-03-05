from .errors import DatabaseError
from .guild import db, insert_guild


def get_alphavantage(id: int) -> str | None:
    """Fetch a guilds Alpha Vantage API key and return it."""

    # find guild or use default if not found
    data = db["Guilds"].find_one(
        {"_id": id},
        {"_id": False, "alphavantagekey": True}
    )

    if data is None:
        data = insert_guild(id=id)

    return data["alphavantagekey"]

def set_alphavantage(id: int, key: str) -> None:
    """Set the publishable API key set for the guild."""

    # add guild if missing
    if db["Guilds"].find_one({"_id": id}) is None:
        insert_guild(id=id)

    response = db["Guilds"].update_one(
        filter={"_id": id},
        update={"$set": {"alphavantagekey": key}}
    )

    if response.modified_count == 0:
        raise DatabaseError("Couldn't set alpha vantage key")
