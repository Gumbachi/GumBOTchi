from common.database import db
from cogs.craigslister.CLQuery import CLQuery

class Craigs:
    def __init__ (self):
        self.active_queries = []
    
    def update(self):
        queries = db.get_queries()
        for query in queries:
            queryObj = CLQuery(
                    uid=query["owner_id"],
                    zip_code=query["zip_code"],
                    state=query["state"],
                    channel=query["channel"],
                    site=query["site"],
                    keywords=query["keywords"],
                    spam_tolerance=query["spam_tolerance"],
                    budget=query["budget"],
                    distance=query["distance"],
                    category=query["category"],
                    has_image=query["has_image"],
                    ping=query["ping"]
                )
            in_mem = False
            for q in self.active_queries:
                if q.to_db() == queryObj.to_db():
                    in_mem = True
                    break
            if not in_mem:
                self.active_queries.append(queryObj)

    def get_user_queries(self, uid):
        queries = []
        for query in self.active_queries:
            if query.owner_id == uid:
                queries.append(query)
        return queries

    async def check_queries(self, bot):
        for query in self.active_queries:
            channel = bot.get_channel(query.channel)
            if channel is None:
                continue 
            ## Search
            listings = query.search()
            ## Filter repeats and spam
            filtered_listings = query.filter_listings(listings)
            if filtered_listings:
                ## Clean leftovers
                clean_listings = query.clean_listings(filtered_listings)
                ## Send them
                await query.send_listings(bot, clean_listings)
                query.update_listings(clean_listings)
                
    def delete_query(self, query):
        db.delete_query(query)
        self.active_queries.remove(query)
        self.update()
    