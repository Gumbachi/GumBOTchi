from pyOfferUp import fetch
from typing import TYPE_CHECKING, List
from cogs.claire.claire_listing import ClaireListing
from dateutil import parser

if TYPE_CHECKING:
    from claire.claire_query import ClaireQuery

class OfferUp:
    
    @classmethod
    def search(cls, query: 'ClaireQuery') -> List[ClaireListing]:
        listings = {}

        # Iterate through keywords and search CL
        for keyword in query.keywords.split(", "):

            posts = fetch.get_listings_by_lat_lon(
                query=keyword,
                lat=query.lat,
                lon=query.lon,
                pickup_distance=query.distance,
                limit=100
            )

            try:
                for post in posts:
                    price = float(post['price'])

                    # Skip if price is less than $5
                    if price < 5:
                        continue

                    # Skip if price exceeds budget
                    if price > query.budget:
                        continue

                    id = post['listingId']
                    if id in listings.keys():
                        continue

                    details = fetch.get_listing_details(id)
                    details = details['data']['listing']
                    listings[id] = ClaireListing(
                            source=cls.__name__,
                            id=details.get("id"),
                            name=details.get('title', 'Unknown?'),
                            url=post['listingUrl'],
                            posted=parser.parse(
                                details.get('postDate', '2001-01-01 00:00')),
                            price=details.get('price'),
                            images=[details.get('photos', [{}])[0].get('detailFull', {}).get('url')],
                            details=details.get('description'),
                            attributes=[
                                f"condition: {details.get('condition')}",
                            ],
                    )

            except Exception as e:
                print(e)

        return list(listings.values())