from craigslist import CraigslistForSale
from common.database import db
from cogs.craigslister.CLQuery import CLQuery
import discord

class Craigs:
    def __init__ (self):
        self.active_queries = []
        self.spam_words = [
            'Smartphones', 'iPhone', 'Samsung', 'LG', 'Android', 'Laptops',
            'Video Games', 'Drones', 'Speakers', 'Cameras',
            'Music Equipment', 'Headsets', 'Airpods', 'https://gameboxhero.com'
            'Top Buyer', 'Quote', 'Sprint', 'ATT', 'Verizon', 'TMobile',
        ]
    
    def search(self, query: CLQuery):
        """Uses the query to search CL. 
        Returns a list of ALL matching posts"""
        listings = []
        # Iterate through keywords and search CL
        for keyword in query.keywords.split(", "):
            # Searches CL with the parameters
            generator = CraigslistForSale(
                site=query.site,
                category=query.category,
                filters={
                    'query': keyword,
                    'max_price': int(query.budget),
                    'has_image': query.has_image,
                    'zip_code': query.zip_code,
                    'search_distance': query.distance,
                    'search_titles': False,
                    'posted_today': True,
                    'bundle_duplicates': True,
                    'min_price': 5
                }
            )

            # Adds listings to a list, include details returns an error if listing doesn't have body
            try:
                for listing in generator.get_results(sort_by='newest', include_details=True):
                    listings.append(listing)
            except Exception as e:
                for listing in generator.get_results(sort_by='newest'):
                    listings.append(listing)
        return listings

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

    async def process_query(self, bot, query: CLQuery):
        ## Search
        listings = self.search(query)
        ## Filter repeats and spam
        filtered_listings = self.filter_listings(listings, query)
        if filtered_listings:
            ## Clean leftovers
            clean_listings = self.clean_listings(filtered_listings)
            ## Send them
            await self.send_listings(bot, clean_listings, query)
            self.update_listings(clean_listings, query)

    async def send_listings(self, bot, listings, query: CLQuery):
        channel = bot.get_channel(query.channel)
        if query.ping:
            user = bot.get_user(query.owner_id)
            await channel.send(f"{user.mention}, here are some new listings for {query.keywords}.")

        for listing in listings:
            display_limit = 350

            # If the body is longer than the display limit, only show the max amount of characters
            body = listing['body']
            if len(body) > display_limit:
                body = f"{body[0:display_limit]}..."

            # Formats and sends the embed
            embed = discord.Embed(
                                title=f"{listing['price']}, {listing['name']}",
                                description=f"{body}\n\n[Link to Craigslist Post]({listing['url']})",
                                color=discord.Color.blue())
            await channel.send(embed=embed)

    def filter_listings(self, listings, query:CLQuery):
        filtered_listings = []
        for listing in listings:
            if listing["id"] not in query.sent_listings:
                if not self.is_spam(listing=listing, query=query):
                    filtered_listings.append(listing)
        return filtered_listings

    def is_spam(self, listing, query: CLQuery):
        spam = 0
        body = listing["body"]
        if len(body) > 500:
            # remove keywords from spam list
            spam_wrds = [i for i in [e.upper() for e in self.spam_words] if i not in [
                j.upper() for j in query.keywords]]
            for word in spam_wrds:
                # -1 means the word is not found
                if body.find(word) != -1:
                    spam += 1
                # Too spammy so break
                if spam > query.spam_tolerance:
                    return True
        return False
    
    def clean_listings(self, listings):
        clean_listings = []
        for listing in listings:
            clean_listing = listing
            if 'body' in clean_listing.keys():
                try:
                    # Removes links and short sentences from the body
                    body = [sentence for sentence in clean_listing['body'].split(
                            '\n') if 'http' not in sentence and len(sentence) > 2]
                    body = '\n'.join(body)
                except:
                    pass
                finally:
                    clean_listing['body'] = body
            else:
                clean_listing['body'] = "Couldn't get details; post was probably deleted."
            clean_listings.append(clean_listing)
        return clean_listings

    def update_listings(self, listings, query: CLQuery):
        for listing in listings:
            query.sent_listings.add(listing["id"])