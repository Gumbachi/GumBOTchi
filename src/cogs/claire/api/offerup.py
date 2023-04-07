from pyOfferUp import fetch
from typing import TYPE_CHECKING, List
from cogs.claire.claire_listing import ClaireListing
from dateutil import parser
from datetime import datetime, timedelta

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

                    # Skip if duplicate
                    id = post['listingId']
                    if id in listings.keys():
                        continue

                    # Load details
                    details = fetch.get_listing_details(id)
                    details = details['data']['listing']

                    posted_date = parser.parse(
                        details.get('postDate', '2001-01-01 00:00')
                    )
                    yesterday = datetime.now()- timedelta(days=1)

                    # When one date is too old, 
                    # the following will too so break out
                    if yesterday.timestamp()  > posted_date.timestamp():
                        break

                    listings[id] = ClaireListing(
                            source=cls.__name__,
                            id=details.get("id"),
                            name=details.get('title', 'Unknown?'),
                            url=post['listingUrl'],
                            posted=posted_date,
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