from typing import TYPE_CHECKING
from .guild import db
if TYPE_CHECKING:
    from cogs.claire.claire_query import ClaireQuery

def insert_query(query: 'ClaireQuery'):
    response = db.Queries.insert_one(query.to_db())
    return response.acknowledged

def delete_query(query: 'ClaireQuery'):
    response = db.Queries.delete_one(query.to_db())
    return response.acknowledged

def get_queries():
    return db.Queries.find({})