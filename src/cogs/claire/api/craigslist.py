from datetime import datetime
from cogs.claire.api.forky_fork.craigslist_headless import CraigslistForSale
from typing import TYPE_CHECKING, List
from cogs.claire.claire_listing import ClaireListing

if TYPE_CHECKING:
    from claire.claire_query import ClaireQuery

class Craigslist:
    
    @classmethod
    def search(cls, query: 'ClaireQuery') -> List[ClaireListing]:
        listings = []

        # Iterate through keywords and search CL
        for keyword in query.keywords.split(", "):

            # Searches CL with the parameters
            generator = CraigslistForSale(
                site=query.site,
                category=query.category,
                filters={
                    'query': keyword,
                    'max_price': query.budget,
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
                    if listing:
                        listings.append(
                            ClaireListing(
                                source=cls.__name__,
                                id=listing.get("id"),
                                name=listing.get('name', 'Unknown?'),
                                url=listing.get('url'),
                                posted=datetime.strptime(
                                    listing.get('created', '2001-01-01 00:00'), '%Y-%m-%d %H:%M'),
                                price=listing.get('price').split("$")[1],
                                images=listing.get('images'),
                                details=listing.get('body'),
                                attributes=listing.get('attrs'),
                            )
                        )

            except Exception as e:
                for listing in generator.get_results(sort_by='newest'):
                    if listing:
                        
                        listings.append(
                            ClaireListing(
                                source=cls.__name__,
                                id=listing.get("id"),
                                name=listing.get('name', 'Unknown?'),
                                url=listing.get('url'),
                                posted=datetime.strptime(
                                    listing.get('created', '2001-01-01 00:00'), '%Y-%m-%d %H:%M'),
                                price=listing.get('price').split("$")[1],
                                images=listing.get('images'),
                                details=listing.get('body'),
                                attributes=listing.get('attrs'),
                            )
                        )

        return listings