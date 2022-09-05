from dataclasses import dataclass, field
from typing import Any

import discord
from craigslist import CraigslistForSale

spam_words = [
    'Smartphones', 'iPhone', 'Samsung', 'LG', 'Android', 'Laptops',
    'Video Games', 'Drones', 'Speakers', 'Cameras',
    'Music Equipment', 'Headsets', 'Airpods', 'https://gameboxhero.com'
    'Top Buyer', 'Quote', 'Sprint', 'ATT', 'Verizon', 'TMobile',
]


@dataclass
class CLQuery:
    owner_id: int
    zipcode: int
    state: str
    channel: int
    site: str
    state: str
    keywords: list[str]
    budget: int = 1000
    distance: int = 30
    category: str = "sss"
    has_image: bool = False
    ping: bool = True
    spam_tolerance: int = 1
    sent_listings: set[int] = field(default_factory=set)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, CLQuery):
            return False
        return self.to_db() == __o.to_db()

    @classmethod
    def from_query(cls, query: dict[str: Any]):
        return cls(
            owner_id=query["owner_id"],
            zipcode=query["zipcode"],
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

    def to_db(self):
        dic = self.__dict__
        dic.pop("sent_listings", None)
        return dic

    def search(self):
        """Uses the query to search CL. 
        Returns a list of ALL matching posts"""
        listings = []
        # Iterate through keywords and search CL
        for keyword in self.keywords:
            # Searches CL with the parameters
            generator = CraigslistForSale(
                site=self.site,
                category=self.category,
                filters={
                    'query': keyword,
                    'max_price': self.budget,
                    'has_image': self.has_image,
                    'zip_code': self.zipcode,
                    'search_distance': self.distance,
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

    async def send_listings(self, bot: discord.Bot, listings):
        channel = bot.get_channel(self.channel)
        if self.ping:
            user = bot.get_user(self.owner_id)
            await channel.send(f"{user.mention}, here are some new listings for {self.keywords}.")

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

    def filter_listings(self, listings):
        filtered_listings = []
        for listing in listings:
            if listing["id"] not in self.sent_listings:
                if not self.is_spam(listing=listing):
                    filtered_listings.append(listing)
        return filtered_listings

    def is_spam(self, listing):
        spam = 0
        body = listing["body"]
        if len(body) > 500:
            # remove keywords from spam list
            spam_wrds = [i for i in [e.upper() for e in spam_words] if i not in [
                j.upper() for j in self.keywords]]
            for word in spam_wrds:
                # -1 means the word is not found
                if body.find(word) != -1:
                    spam += 1
                # Too spammy so break
                if spam > self.spam_tolerance:
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

    def update_listings(self, listings):
        for listing in listings:
            self.sent_listings.add(listing["id"])
