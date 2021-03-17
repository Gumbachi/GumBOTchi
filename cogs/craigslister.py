from craigslist import CraigslistForSale
from discord.ext import commands

class Craigslister(commands.Cog):
    """Hold and executes all sbonk commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='craigslistme')
    async def craigslist_me_daddy(self, ctx, site, max_price, zip_code, distance, has_image, *, keywords):
        keywords = keywords.split(' ')
        sent_listings = []
        self.create_query(site, max_price, zip_code, distance, has_image, keywords, sent_listings)

    @commands.command(name='uncraigslistme')
    async def uncraigslist_me_daddy(self, ctx):
        ## Deletes craigslist query for user
        return

    def create_query(self, site, max_price, zip_code, distance, has_image, keywords, sent_listings):



    def loop(self):
        users = []
        for user in users:
            queries = user.get_queries()
            for query in queries:
                listings = self.search(query)
                for listing in listings:
                    self.send_listing(listing)

    def search(self, **data):
        listings = [] # List to store results of search
        keywords = data.get('keywords')
        # Searches CL with the parameters
        for keyword in keywords:
            generator = CraigslistForSale(  site=data.get('site'),
                                            filters={ 
                                                    'query': keyword,
                                                    'max_price': data.get('max_price'),
                                                    'posted_today': True, 
                                                    'bundle_duplicates': True, 
                                                    'has_image': data.get('has_image'), 
                                                    'search_titles': False,                                  
                                                    'zip_code': data.get('zip_code'), 
                                                    'search_distance': data.get('distance'),     
                                                    })
            
            # Adds listings to a list, include details returns an error if listing doesn't have body
            try:
                listings.append([obj for obj in generator.get_results(sort_by='newest', include_details=True)])
            except:
                listings.append([obj for obj in generator.get_results(sort_by='newest')])

        sent_listings = data.get('sent_listings')
        listings = self.clean_list(sent_listings, listings)

        return listings

    def send_listing(self, listing, channel=821832364123750430):
        u = bot.get_channel(channel)
        alert = "Possible Steal! " if int(result['price'].replace("$", "")) < 25 else ''
        if 'body' in listing.keys():
            try:
                body = [sentence for sentence in listing['body'].split('\n') if 'http' not in sentence and len(sentence) > 2]
                body = '\n'.join(body)
            except: body = listing['body']
            if len(body) > 1500:
                body = body[0:1500] + ' ...'
            await u.send(embed= discord.Embed(  title = f"{alert}{listing['price']}, {listing['name']}", 
                                                description = f"{body}\n\n[Link to Craigslist Post]({listing['url']})", 
                                                color = discord.Color.red(),)
                )
        else:
            await u.send(embed= discord.Embed(  title = f"{alert}{listing['price']}, {listing['name']}", 
                                                description = f"Couldn't get details; post might have been deleted. \n\n[Link to Craigslist Post]({result['url']})", 
                                                color = discord.Color.green(),)
                )

    def clean_list(self, sent_listings, new_listings):
        clean_listings = []
        for listing in new_listings:
            if listing not in sent_listings:
                clean_listings.append(listing)
                #TODO append to sent_list in DB
        
        return clean_listings       

    def search(self):
        site = [] # Craigslist site
        keywords = [] # Words to search for
        max_price = [] # Max price
        has_image = [] # Whether a listing must have an image to show up
        zip_code = [] # Your zip code
        distance = [] # Max distance of a listing

def setup(bot):
    bot.add_cog(SbonkCommands(bot))
