import discord
from common.database import db

from .clquery import CLQuery


class Craigs:
    def __init__(self):
        self.active_queries: list[CLQuery] = []

    def update(self):
        queries = db.get_queries()
        for query in queries:
            clquery = CLQuery.from_query(query)

            if clquery not in self.active_queries:
                self.active_queries.append(clquery)

    def get_user_queries(self, owner_id: int):
        return [query for query in self.active_queries if query.owner_id == owner_id]

    async def check_queries(self, bot: discord.Bot):
        for query in self.active_queries:
            channel = bot.get_channel(query.channel)
            if channel is None:
                continue

            listings = query.search()

            # Filter repeats and spam
            filtered_listings = query.filter_listings(listings)
            if filtered_listings:
                # Clean leftovers
                clean_listings = query.clean_listings(filtered_listings)
                # Send them
                await query.send_listings(bot, clean_listings)
                query.update_listings(clean_listings)

    def delete_query(self, query: CLQuery):
        db.delete_query(query)
        self.active_queries.remove(query)
        self.update()
