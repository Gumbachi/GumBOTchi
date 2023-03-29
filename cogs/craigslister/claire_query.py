from craigslist_headless import CraigslistForSale
from dataclasses import dataclass, field
from typing import List
import discord

spam_words = [
    'Smartphones', 'iPhone', 'Samsung', 'LG', 'Android', 'Laptops',
    'Video Games', 'Drones', 'Speakers', 'Cameras',
    'Music Equipment', 'Headsets', 'Airpods', 'https://gameboxhero.com'
    'Top Buyer', 'Quote', 'Sprint', 'ATT', 'Verizon', 'TMobile',
]

@dataclass(slots=True)
class ClaireQuery:
    owner_id: int
    zip_code: int
    state: str
    channel: int
    site: str
    state: str
    keywords: str
    budget: int = 1000
    distance: int = 30
    category: str = "sss"
    has_image: bool = False
    ping: bool = True
    spam_tolerance: int = 5
    sent_listings: set = field(default_factory=set)

    def to_db(self) -> dict:
        """Converts Claire Query to JSON for DB"""

        final_dic = {}
        for attr in self.__slots__:
            if attr not in ["sent_listings"]:
                final_dic[attr] = self.__getattribute__(attr)
        return final_dic

    def search(self) -> List[dict]:
        """Uses the query to search Craigslist. 
        Returns a list of ALL matching posts"""

        listings = []

        # Iterate through keywords and search CL
        for keyword in self.keywords.split(", "):

            # Searches CL with the parameters
            generator = CraigslistForSale(
                site=self.site,
                category=self.category,
                filters={
                    'query': keyword,
                    'max_price': self.budget,
                    'has_image': self.has_image,
                    'zip_code': self.zip_code,
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

    def filter_listings(self, listings: List[dict]) -> List[dict]:
        """Filters listings down to the ones that are not spam
        and the ones that have not been sent."""

        filtered_listings = []
        for listing in listings:

            # Not sent
            if listing["id"] not in self.sent_listings:

                # Not Spam
                if not self.is_spam(listing=listing):
                    filtered_listings.append(listing)

        return filtered_listings

    def is_spam(self, listing: dict) -> bool:
        """Checks listing for spam words, \
        if it passes the tolerance then it's omitted"""

        spam = 0
        body = listing["body"]

        # Only check posts with long descriptions
        if len(body) > 500:

            # Remove keywords from spam list
            spam_words = [i for i in [e.upper() for e in spam_words] if i not in [
                j.upper() for j in self.keywords]]
            
            for word in spam_words:

                # -1 means the word is not found
                if body.find(word) != -1:
                    spam += 1
                
                # Too spammy so break
                if spam > self.spam_tolerance:
                    return True

        return False

    def clean_listings(self, listings: List[dict]) -> List[dict]:
        """Cleans up the listings to prepare for sending."""

        clean_listings = []
        for listing in listings:
            clean_listing = listing
            if 'body' in clean_listing.keys():
                try:
                    # Removes links and short sentences from the body
                    body = [sentence for sentence in clean_listing['body'].split(
                            '\n') if 'http' not in sentence and len(sentence) > 2]
                    body = '\n'.join(body)
                except Exception as e:
                    print("Error", e)
                finally:
                    clean_listing['body'] = body
            else:
                clean_listing['body'] = "Couldn't get details; post was probably deleted."
            clean_listings.append(clean_listing)

        return clean_listings

    def mark_sent(self, listings: List[dict]):
        for listing in listings:
            self.sent_listings.add(listing["id"])

    async def send_listings(self, bot, listings):
        """ Sends the listings"""

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
                color=discord.Color.blue()
            )

            await channel.send(embed=embed)