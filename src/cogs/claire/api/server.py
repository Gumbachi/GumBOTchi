from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from datetime import datetime

import sys
sys.path.append('/app/src/')
load_dotenv()

from cogs.claire.api.modules.maps import get_lat_lon  # noqa: E402
from cogs.claire.claire_model import Claire, ClaireQuery # noqa: E402
from database.claire import delete_query, insert_query # noqa: E402

app = FastAPI()
claire = Claire()
claire.update()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/add_query/")
async def add_query(
        uid: int,
        channel_id: int,
        zip_code: int,
        state: str,
        site: str,
        budget: float,
        keywords: str,
        distance: int,
        has_image: bool,
        spam_probability: float,
        ping: bool,
        category: str,
    ):

    lat, lon = get_lat_lon(zip_code)
    new_query = ClaireQuery(
        owner_id= uid,
        zip_code=zip_code,
        state=state,
        channel=channel_id,
        site = site,
        lat=lat,
        lon=lon,
        keywords=keywords,
        spam_probability=spam_probability,
        budget=budget,
        distance=distance,
        category=category,
        has_image=has_image,
        ping=ping
    )
    
    try:
        new_query.search() # Dummy search to see if it works
    except Exception as e:
        return {
            "message" : "Invalid query please double check your parameters",
            "error": e
        }

    result = insert_query(new_query)

    if result:
        claire.active_queries.append(new_query)
        claire.update()
        return {"message" : "Added."}
    else:
        return {"message" : "Failed to add to DB. Try again later."}
    
@app.get("/claire_queries/")
async def show_queries(uid: int):
    queries = claire.get_user_queries(uid)
    return {
        "queries" : queries
    }

@app.get("/delete_query/")
async def unclaireme(uid: int, index: int):
    queries = claire.get_user_queries(uid)
    to_delete = queries[index-1]
    result = delete_query(to_delete)
    if result:
        claire.active_queries.remove(to_delete)
        claire.update()

    return {"message" : "Query removed." if result else "Unable to delete, try again."}

@app.get("/search/")
async def search():
    new_listings = claire.check_queries()

    return {
        'time' : datetime.now(),
        'results' : new_listings
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)