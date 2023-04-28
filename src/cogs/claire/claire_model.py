from typing import List

from database.claire import get_queries, delete_query
from cogs.claire.claire_query import ClaireQuery
from cogs.claire.ml.claire_ml import ClaireSpam
from cogs.claire.api.forky_fork.craigslist_headless.browser import CraigslistBrowser

class Claire:
    """Holds all of the queries for Claire Session"""
    def __init__ (self):
        self.active_queries: List[ClaireQuery] = []
        self.spam_model = ClaireSpam()
    
    def update(self):
        """Fetches latest queries from DB, creates custom query objects and check
        if the object is already being tracked in memory"""

        queries = get_queries()
        for query in queries:
            in_memory = False

            try:
                query_obj = ClaireQuery(
                        owner_id=query["owner_id"],
                        zip_code=query["zip_code"],
                        lat=query["lat"],
                        lon=query["lon"],
                        state=query["state"],
                        channel=query["channel"],
                        site=query["site"],
                        keywords=query["keywords"],
                        spam_probability=query["spam_probability"],
                        budget=query["budget"],
                        distance=query["distance"],
                        category=query["category"],
                        has_image=query["has_image"],
                        ping=query["ping"]
                )
            except Exception as e:
                print(f'Corrupted query skipping... {e}')
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

    def check_queries(self) -> List[dict]:
        """Searches for new results in tracked queries"""
        new_listings = []
        for query in self.active_queries:

            # Search
            listings = query.search()

            # Filter and spam
            filtered_listings = query.filter_listings(
                spam_model=self.spam_model,
                listings=listings
            )

            if filtered_listings:

                # Clean
                clean_listings = query.clean_listings(filtered_listings)

                for listing in clean_listings:
                    listing.set_spam_score(self.spam_model)

                new_listings.append(
                    {
                        'query' : query,
                        'listings' : clean_listings
                    }
                )

                # Mark as sent
                query.mark_sent(clean_listings)
        
        CraigslistBrowser.quit()
        return new_listings
                
    def delete_query(self, query: ClaireQuery):
        """Nukes query from existence"""

        # Delete from DB
        delete_query(query)

        # Remove from tracked
        self.active_queries.remove(query)

        # Update to latest
        self.update()
    