import asyncio
import datetime
import re

import common.database as db
import discord
from common.cfg import get_prefix
from craigslist import CraigslistForSale
from discord.ext import commands


class Craigslister(commands.Cog):
    """Hold and executes all craigslisting commands."""

    def __init__(self, bot):
        self.bot = bot 

        # Internal counter for generating IDs
        self.count = 1

    def cog_check(self, ctx):
        if not db.users.find_one({"_id": ctx.author.id}):
            data = {
                "_id": ctx.author.id,
                "zipcode": None,
                "site": None,
                "clqueries": []
            }
            db.users.insert_one(data)
        return True

    @commands.command(name="clhelp", aliases=["clhalp"])
    async def cl_halp(self, ctx):
        """Help command. Shows users how to use the CL functions"""
        prefix = get_prefix(self.bot, ctx.message)
        body = f"""\n\nFirst you're going to want to set your zip and site using the setup commands.\n\n1.    {prefix}setzip 12345\n\n2. {prefix}setsize nameofsite. \n\nTo get the right site, visit https://www.craigslist.org/about/sites, click on the best location, and copy the site in the URL for example for Washington DC the URL is https://**washingtondc**.craigslist.org/ so the site would be washingtondc, for NYC it would be newyork.\n\nAfter you set your zip and site, you're ready to add queries.\n\nTo add a query simply use the {prefix}clmedaddy command with the proper syntax. Eg. {prefix}clmedaddy [Apple TV, Apple, TV] 200 30 No Pingme.\n\nThe order of the arguments is as follows: keywords in brackets and separated by a comma and a space like this: [Apple TV, Apple, TV], then the max price you're willing to pay, no currency symbols. Followed by the distance you're willing to travel. Whether the craigslist post should include pictures of the item, and whether you want to be pinged every time one or more new items match your parameters. In the example, I am looking for listings that match Apple TV, Apple, or TV, are no more than $200 are less than 30 miles away they do not need to include a picture, but may, and I want to be pinged.\n\nTo see your queries use {prefix}clinfo, and to remove a query use {prefix}unclmedaddy and the number of the query (this can be seen by using {prefix}clinfo) eg. {prefix}unclmedaddy 2.\n\nThe bot will automatically check for new listings every 5 minutes and you may not have more than 3 queries active at a time.""" 
        embed=discord.Embed(title=f"Welcome to Craigslister!",
                            description=body,
                            color=discord.Color.blue())
        embed.set_footer(text="Godspeed")
        return await ctx.channel.send(embed=embed)

    # Setup Commands
    @commands.command(name="setzip", aliases=["zip", "zipcode", "setzipcode"])
    async def set_user_zip(self, ctx, zipcode: int):
        """Updates a user's zip code"""
        db.users.update_one(
            {"_id": ctx.author.id},
            {"$set": {"zipcode": zipcode}}
        )
        return await ctx.channel.send(f"Zip updated to: {zipcode}")

    @commands.command(name="setsite", aliases=["site"])
    async def set_user_site(self, ctx, site):
        """Updates a user's CL site"""
        db.users.update_one(
            {"_id": ctx.author.id},
            {"$set": {"site": site}}
        )
        return await ctx.channel.send(f"Site updated to: {site}")

    @commands.command(name='craigslistme', aliases=["clme", "addquery", "addq", "clmedaddy"])
    async def craigslist_me_daddy(self, ctx, *, query):
        """It craigslists. Input syntax: !clme [Apple TV, Apple, TV] 200 30 yeet pingme"""

        # Check if the user has more than the max number of queries allowed
        max_queries = 3
        queries = db.userget(ctx.author.id, 'clqueries')
        if len(queries) >= max_queries:
            return await ctx.channel.send("You can only have 3 active queries at one time.")

        # Processes the input into usable variables, max keywords 
        # modifies the maximum number of keywords allowed ber query
        max_keywords = 5
        try:
        
            query = query.split(']')
            keywords = query[0][1:].split(", ")
            if len(keywords) > max_keywords:
                return await ctx.channel.send(f"Queries can only have up to {max_keywords} key words.")
            rest = query[1][1:].split(" ")
            max_price = rest[0]
            distance = rest[1]
        except:
            raise commands.CommandError(f"Invalid query, please refer to {get_prefix(self.bot, ctx.message)}clhelp for syntax")

        # Checks if has_image and pingme were provided as args and sets them accordingly
        try:
            has_image = rest[2]
        except:
            has_image = "no"
        try:
            pingme = rest[3]
            if pingme.lower() in ("pingme", "ping"):
                pingme = ctx.message.author.id
        except:
            pingme = False

        try:
            category = rest[4]
        except:
            category = "sss"

        # Generates query ID
        query_id = self.id_maker()

        # Formats the new query for the DB
        new_query = {
            "_id": query_id,
            "max_price": abs(float(max_price)),
            "distance": abs(float(distance)),
            "has_image": has_image.lower() in ("yes", "true", "yeet", "yaya"),
            "keywords": keywords,
            "sent_listings": [],
            "channel": ctx.channel.id,
            "ping": pingme,
            "category": category
        }

        # Updates DB
        db.users.update_one(
            {"_id": ctx.author.id},
            {"$push": {"clqueries": new_query}}
        )
        return await ctx.channel.send("SUCCessfully added.")

    @commands.command(name='uncraigslistme', aliases=["unclemedaddy", "deletequery", "delq"])
    async def uncraigslist_me_daddy(self, ctx, number: int):
        """Deletes specified craigslist query"""

        try:
            queries = db.userget(ctx.author.id, 'clqueries')
            db.users.update_one(
                {"_id": ctx.author.id},
                {"$pull": {"clqueries": queries[number-1]}}
            )
            return await ctx.channel.send("Query removed.")
        except:
            return await ctx.channel.send("There was a problem.")

    @commands.command(name='clinfo')
    async def my_queries(self, ctx):
        """Displays active queries for user"""

        queries = db.userget(ctx.author.id, 'clqueries')
        if not queries:
            return await ctx.channel.send("You don't have any queries")
        
        # Formats and sends the active queries as an embed
        current_queries = ""
        for i, query in enumerate(queries):
            current_queries = f"""{current_queries}{i+1}. "{', '.join(query['keywords'])}" | Max Price: ${query['max_price']} | Ping: {bool(query['ping'])}\n"""

        embed=discord.Embed(title=f"Craigslisting for {ctx.author.nick}",
                            description=f"{ctx.author.mention}\n\n{current_queries}",
                            color=discord.Color.blue())
        return await ctx.channel.send(embed=embed)

    async def loop(self):
        """Searches CL every X amount of minutes (determined by check_time) for every query that every user has"""

        check_time = 5
        while True:
            users = db.users.find({})

            # Iterate through every user with queries
            for user in users:
                _id = user['_id']
                zip_code = user['zipcode']
                site = user['site']

                # If the user has not set their site or zip, skip them
                if not site or not zip_code:
                    continue
                
                # Iterate through the users queries
                queries = user['clqueries']
                for query in queries:
                    channel = self.bot.get_channel(query['channel'])

                    # Search, then clean, then update
                    listings = self.search(site, zip_code, query)
                    listings, updated_list = self.clean_list(query['sent_listings'], listings)
                    self.update_sent_listings(_id, query['_id'], updated_list)

                    # If there are no new listings skip this query otherwise ping and send them
                    if not listings:
                        continue

                    # Ping if user requested ping
                    if query['ping']:
                        user = self.bot.get_user(query['ping'])
                        await channel.send(f"{user.mention}, here are some new listings for {', '.join(query['keywords'])}.")
                    
                    # Send it
                    for listing in listings:
                        await self.send_listing(listing, channel)

            print("Done searching")
            # Sleeps for 60 seconds * the specified number of minutes
            await asyncio.sleep(60*check_time)

    def search(self, site, zip_code, query):
        """Uses the query to search CL. 
        Returns a list of ALL matching posts"""

        listings = []

        # Iterate through keywords and search CL
        for keyword in query['keywords']:
            # Searches CL with the parameters
            generator = CraigslistForSale(
                site=site,
                category=query['category'],
                filters={
                    'query': keyword,
                    'max_price': int(query['max_price']),
                    'posted_today': True,
                    'bundle_duplicates': True,
                    'has_image': query['has_image'],
                    'search_titles': False,
                    'zip_code': zip_code,
                    'search_distance': int(query['distance']),
                }
            )

            # Adds listings to a list, include details returns an error if listing doesn't have body
            try:
                for listing in generator.get_results(sort_by='newest', include_details=True):
                    listings.append(listing)
            except:
                for listing in generator.get_results(sort_by='newest'):
                    listings.append(listing)

        return listings
    
    def clean_list(self, sent_listings, new_listings):
        """Verifies that the listings provided have not been sent already. 
        Returns list of postings and an updated list of ids that have already been processed"""

        if not new_listings:
            return (None, None)

        clean_listings = []
        updated_list = sent_listings

        # Check that the listings have not been sent already, 
        # if they haven't, add them to clean listings and add 
        # the id to the list of IDs to be updated later
        for listing in new_listings:
            if listing['id'] not in sent_listings:
                clean_listings.append(listing)
                updated_list.append(listing['id'])

        return (clean_listings, updated_list)

    def update_sent_listings(self, user_id, query_id, updated_list):
        """Updates the sent listings for a query"""
        db.users.update_one(
                    {"_id": user_id, "clqueries._id": query_id},
                    {"$set": {"clqueries.$.sent_listings": updated_list}}
                )

    async def send_listing(self, listing, channel):
        """Takes a listing object and sends it to the specified channel"""
        
        display_limit = 350

        # Check if the listing has a body, no body usually means the post no longer exists
        if 'body' in listing.keys():
            try:
                # Removes links and short sentences from the body
                body = [sentence for sentence in listing['body'].split(
                    '\n') if 'http' not in sentence and len(sentence) > 2]
                body = '\n'.join(body)
            except:
                body = listing['body']
            
            # If the body is longer than the display limit, only show the max amount of characters
            if len(body) > display_limit:
                body = f"{body[0:display_limit]}..."
            
            # Green because the post probably still exists
            color = discord.Color.green()
        else:
            # No body, post was probably deleted, and so the color is red
            body = "Couldn't get details; post was probably deleted."
            color = discord.Color.red()

        # Formats and sends the embed
        embed=discord.Embed(title=f"{listing['price']}, {listing['name']}",
                            description=f"{body}\n\n[Link to Craigslist Post]({listing['url']})",
                            color=color)
        return await channel.send(embed=embed)
    
    def id_maker(self):
        """Generates an ID based on the date and an internal counter.
        Heroku's etheral filesystem make it so there could be duplicate 
        IDs and that is why a while loop is needed."""

        date = datetime.datetime.now()

        # Loop until it finds an ID that does not exist
        while True:
            # Generates an ID and adds one to the internal counter for future IDs
            query_id = int(f"{date.day}{date.month}{date.year}{self.count}")
            self.count += 1

            # Tries to find a matching ID in the DB, 
            # if it finds a match there won't be a key error,
            # if there's a match the key error will break the loop
            try:
                db.users.find_one({"clqueries._id": query_id})['clqueries']
            except:
                break
        
        return query_id

def setup(bot):
    bot.add_cog(Craigslister(bot))
