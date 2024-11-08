from .errors import PogDatabaseError
from .guild import db, insert_guild

response_cache: dict[int, list[str]] = {}
activator_cache: dict[int, list[str]] = {}


def get_pogresponses(id: int, from_cache=True) -> list[str]:
    """Fetch pog responses for a guild and add guilds if not exists"""

    # check for colors in cache
    if id in response_cache and from_cache:
        return response_cache[id]

    # find guild or use default if not found
    data = db["Guilds"].find_one({"_id": id}, {"_id": False, "pogresponses": True})

    if data is None:
        data = insert_guild(id=id)

    # update cache
    response_cache[id] = data["pogresponses"]

    return data["pogresponses"]


def add_pogresponse(id: int, response: str) -> None:
    """Add a pog response to the db."""

    if not isinstance(response, str) or not response:
        raise PogDatabaseError("Invalid pog response")

    # add guild if missing
    if id not in response_cache and db["Guilds"].find_one({"_id": id}) is None:
        insert_guild(id=id)

    result = db["Guilds"].update_one(
        filter={"_id": id}, update={"$addToSet": {"pogresponses": response}}
    )

    if result.modified_count == 0:
        raise PogDatabaseError(
            "Couldn't add pog response", "Typically due to a duplicate response"
        )

    # update cache
    if id in response_cache:
        response_cache[id].append(response)


def remove_pogresponse(id: int, response: str):
    """Remove a pog response from the db."""

    # add guild if missing
    if id not in response_cache and db["Guilds"].find_one({"_id": id}) is None:
        insert_guild(id=id)

    result = db["Guilds"].update_one(
        filter={"_id": id}, update={"$pull": {"pogresponses": response}}
    )

    if result.modified_count == 0:
        raise PogDatabaseError("Couldn't remove pog response")

    # update cache
    if id in response_cache:
        response_cache[id].remove(response)


def get_pogactivators(id: int, from_cache=True) -> list[str]:
    """Fetch pog activators for a guild and add guilds if not exists"""

    # check for colors in cache
    if id in activator_cache and from_cache:
        return activator_cache[id]

    # find guild or use default if not found
    data = db["Guilds"].find_one({"_id": id}, {"_id": False, "pogactivators": True})

    if data is None:
        data = insert_guild(id=id)

    # update cache
    activator_cache[id] = data["pogactivators"]

    return data["pogactivators"]


def add_pogactivator(id: int, activator: str) -> None:
    """Add a pog activator to the db."""

    if not isinstance(activator, str) or not activator:
        raise PogDatabaseError("Invalid pog activator")

    # add guild if missing
    if id not in response_cache and db["Guilds"].find_one({"_id": id}) is None:
        insert_guild(id=id)

    result = db["Guilds"].update_one(
        filter={"_id": id}, update={"$addToSet": {"pogactivators": activator}}
    )

    if result.modified_count == 0:
        raise PogDatabaseError(
            "Couldn't add pog activtor", "Typically due to a duplicate"
        )

    # update cache
    if id in activator_cache:
        activator_cache[id].append(activator)


def remove_pogactivator(id: int, activator: str):
    """Remove a pog activator from the db."""

    # add guild if missing
    if id not in response_cache and db["Guilds"].find_one({"_id": id}) is None:
        insert_guild(id=id)

    result = db["Guilds"].update_one(
        filter={"_id": id}, update={"$pull": {"pogactivators": activator}}
    )

    if result.modified_count == 0:
        raise PogDatabaseError("Couldn't remove pog activator")

    # update cache
    if id in activator_cache:
        activator_cache[id].remove(activator)
