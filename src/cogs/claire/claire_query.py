from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
from cogs.claire.api.sources import Sources

if TYPE_CHECKING:
    from claire_listing import ClaireListing
    from cogs.claire.ml.claire_ml import ClaireSpam

@dataclass(slots=True)
class ClaireQuery:
    owner_id: int
    zip_code: int
    state: str
    channel: int
    site: str
    state: str
    lat: float
    lon: float
    keywords: str
    budget: int = 1000
    distance: int = 30
    category: str = "sss"
    has_image: bool = False
    ping: bool = True
    spam_probability: int = 80
    sent_listings: set = field(default_factory=set)

    def to_db(self) -> dict:
        """Converts Claire Query to JSON for DB"""

        final_dic = {}
        for attr in self.__slots__:
            if attr not in ["sent_listings"]:
                final_dic[attr] = self.__getattribute__(attr)
        return final_dic

    def search(self) -> List['ClaireListing']:
        """Uses the query to search Craigslist. 
        Returns a list of ALL matching posts"""

        listings: List['ClaireListing'] = []

        for source in Sources:
            if source.is_valid():
                source_listings = source.value.search(query=self)
                listings += source_listings

        return listings

    def filter_listings(
            self,
            spam_model: 'ClaireSpam',
            listings: List['ClaireListing']
            ) -> List['ClaireListing']:
        """Filters listings down to the ones that are not spam
        and the ones that have not been sent."""

        filtered_listings: List['ClaireListing'] = []
        for listing in listings:
            
            # skip if sent
            if listing.id in self.sent_listings:
                continue

            # skip if spam Spam
            if self.is_spam(
                spam_model=spam_model,
                listing=listing
            ):
                continue

            filtered_listings.append(listing)

        return filtered_listings

    def is_spam(
            self,
            spam_model: 'ClaireSpam',
            listing: 'ClaireListing'
            ) -> bool:
        """
        If the probability that a listing is spam
        exceeds the threshold, it is flagged as spam
        """

        prob_spam = spam_model.probability_of_spam(listing.body) * 100
        if prob_spam > self.spam_probability:
            return True
        
        return False
        
        # spam_words = [
        #     'Smartphones', 'iPhone', 'Samsung', 'LG', 'Android', 'Laptops',
        #     'Video Games', 'Drones', 'Speakers', 'Cameras',
        #     'Music Equipment', 'Headsets', 'Airpods', 'https://gameboxhero.com'
        #     'Top Buyer', 'Quote', 'Sprint', 'ATT', 'Verizon', 'TMobile',
        # ]

        # spam = 0
        # body = listing.details

        # # Only check posts with long descriptions
        # if len(body) > 500:

        #     # Remove keywords from spam list
        #     spam_words = [i for i in [e.upper() for e in spam_words] if i not in [
        #         j.upper() for j in self.keywords]]
            
        #     for word in spam_words:

        #         # -1 means the word is not found
        #         if body.find(word) != -1:
        #             spam += 1
                
        #         # Too spammy so break
        #         if spam > self.spam_tolerance:
        #             return True

        # return False

    def clean_listings(self, listings: List['ClaireListing']) -> List['ClaireListing']:
        """Cleans up the listings to prepare for sending."""

        clean_listings = []
        for listing in listings:
            listing.clean()
            clean_listings.append(listing)

        return clean_listings

    def mark_sent(self, listings: List['ClaireListing']):
        for listing in listings:
            self.sent_listings.add(listing.id)

    async def send_listings(self, bot, listings: List['ClaireListing']):
        """ Sends the listings"""

        channel = bot.get_channel(self.channel)
        if self.ping:
            user = bot.get_user(self.owner_id)
            await channel.send(f"{user.mention}, here are some new listings for {self.keywords}.")

        for listing in listings:
            embed = listing.discord_embed()
            await channel.send(embed=embed)