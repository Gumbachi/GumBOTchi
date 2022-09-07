from .errors import DatabaseError
from .guild import db, insert_guild


def get_iexkey(id: int) -> str | None:
    """Fetch a guilds IEX API key and return it."""

    # find guild or use default if not found
    data = db.Guilds.find_one(
        {"_id": id},
        {"_id": False, "iexkey": True}
    )

    if data is None:
        data = insert_guild(id=id)

    return data["iexkey"]


def set_iexkey(id: int, key: str):
    """Set the publishable API key set for the guild."""

    # add guild if missing
    if db.Guilds.find_one({"_id": id}) is None:
        insert_guild(id=id)

    response = db.Guilds.update_one(
        filter={"_id": id},
        update={"$set": {"iexkey": key}}
    )

    if response.modified_count == 0:
        raise DatabaseError("Couldn't set IEX key")
