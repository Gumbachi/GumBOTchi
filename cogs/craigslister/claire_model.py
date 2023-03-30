from common.database import db
from cogs.craigslister.claire_query import ClaireQuery
from typing import List

class Claire:
    """Holds all of the queries for Claire Session"""
    def __init__ (self):
        self.active_queries: List[ClaireQuery] = []
    
    def update(self):
        """Fetches latest queries from DB, creates custom query objects and check
        if the object is already being tracked in memory"""

        queries = db.get_queries()
        for query in queries:
            in_memory = False

            try:
                query_obj = ClaireQuery(
                        owner_id=query["owner_id"],
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
            except Exception as e:
                print('Corrupted query skipping...', e)
                continue
            
            # Check if it's already in memory
            for q in self.active_queries:
                if q.to_db() == query_obj.to_db():
                    in_memory = True
                    break

            # Track query if not in memory
            if not in_memory:
                self.active_queries.append(query_obj)

    def get_user_queries(self, uid: str) -> List[ClaireQuery]:
        """Gets queries for specified user"""
        return [query for query in self.active_queries if query.owner_id == uid]

    async def check_queries(self, bot):
        """Searches for new results in tracked queries"""
        for query in self.active_queries:
            channel = bot.get_channel(query.channel)
            if channel is None:
                continue 

            # Search
            listings = query.search()

            # Filter and spam
            filtered_listings = query.filter_listings(listings)
            if filtered_listings:

                # Clean
                clean_listings = query.clean_listings(filtered_listings)

                # Send
                await query.send_listings(bot, clean_listings)

                # Mark as sent
                query.mark_sent(clean_listings)
                
    def delete_query(self, query: ClaireQuery):
        """Nukes query from existence"""

        # Delete from DB
        db.delete_query(query)

        # Remove from tracked
        self.active_queries.remove(query)

        # Update to latest
        self.update()
    