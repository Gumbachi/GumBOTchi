from craigslist import CraigslistForSale
from discord.ext import commands
import datetime
import re, discord
import asyncio
from common.cfg import get_prefix

import common.database as db

class Craigslister(commands.Cog):
    """Hold and executes all sbonk commands."""

    def __init__(self, bot):
        self.bot = bot 
        self.count = 123

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
        prefix = get_prefix(self.bot, ctx.message)
        await ctx.channel.send(
            f"""
            ```Welcome to Craigslister! \n\nFirst you're going to want to set your zip and site using {prefix}setzip 12345 and {prefix}setsize nameofsite. \n\nTo get the right site, visit https://www.craigslist.org/about/sites, click on the best location, and copy the site in the URL for example for Washington DC. the URL is https://**washingtondc**.craigslist.org/ so the site would be washingtondc, for NYC it would be newyork. etc. \n\nAfter you set your zip and site, you're ready to start. To add a query simply use the {prefix}clmedaddy command with the proper syntax. Eg. {prefix}clmedaddy "Apple TV, Apple, TV" 200 30 No Pingme. \n\nThe order of the arguments is as follows, keywords surrounded by parenthesis and separated by a comma and a space ("Apple TV, Apple, TV"), then the max price you're willing to pay, no dollar signs or anything like that. Followed by the distance you're willing to travel. Whether the craigslist post should include pictures of the item, and whether you want to be pinged everytime a new item matches your parameters. In the example, I am looking for listings that match Apple TV, Apple, or TV, are no more than $200 are less than 30 miles away they do not need to include a picture, but may, and I want to be pinged. \n\nTo see your queries use {prefix}clinfo, and to remove a query use {prefix}unclmedaddy and the number of the query (this can be seen by using {prefix}clinfo) eg. {prefix}unclmedaddy 2. \n\nThe bot will automatically check for new listings every 5 minutes and you may not have more than 3 queries active at a time. \n\nGodspeed.```
            """   
            )

    # Setup Commands
    @commands.command(name="setzip", aliases=["zip", "zipcode", "setzipcode"])
    async def set_user_zip(self, ctx, zipcode: int):
        db.users.update_one(
            {"_id": ctx.author.id},
            {"$set": {"zipcode": zipcode}}
        )
        return await ctx.channel.send(f"Zip updated to: {zipcode}")

    @commands.command(name="setsite", aliases=["site"])
    async def set_user_site(self, ctx, site):
        db.users.update_one(
            {"_id": ctx.author.id},
            {"$set": {"site": site}}
        )
        return await ctx.channel.send(f"Site updated to: {site}")

    @commands.command(name='craigslistme', aliases=["clme", "addquery", "addq", "clmedaddy"])
    async def craigslist_me_daddy(self, ctx, *, query):
        """It craigslists."""
        # Example !clme "Apple TV, Apple, TV" 200 30 yeet pingme
        queries = db.userget(ctx.author.id, 'clqueries')
        if len(queries) >= 3:
            return await ctx.channel.send("You can only have 3 active queries at one time.")

        try:
            query = query.split('"')
            keywords = query[1].split(", ")
            if len(keywords) > 5:
                return await ctx.channel.send("Queries can only have up to 5 key words.")
            rest = query[2][1:].split(" ")
            max_price = rest[0]
            distance = rest[1]
        except:
            prefix = '$'
            return await ctx.channel.send(
                f'Invalid query, please format the query exacty as shown here: \
                    {prefix}clme "Key words 1, Key word 2, keyword 3, etc" max_price max_distance only_show_posts_with_pictures(Yes/No) pingme. \
                    Eg. !clme "Apple TV, Apple, TV" 200 30 yes pingme')

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

        while True:
            query_id = self.id_maker()
            queries = db.users.find_one({"clqueries._id": query_id})
            try:
                queries = queries['clqueries']
            except:
                break
            count = 0
            for q in queries:
                if q['_id'] == query_id:
                    count += 1
            if not count:
                break

        new_query = {
            "_id": query_id,
            "max_price": abs(float(max_price)),
            "distance": abs(float(distance)),
            "has_image": has_image.lower() in ("yes", "true", "yeet", "yaya"),
            "keywords": keywords,
            "sent_listings": [],
            "channel": ctx.channel.id,
            "ping": pingme
        }

        db.users.update_one(
            {"_id": ctx.author.id},
            {"$push": {"clqueries": new_query}}
        )

        return await ctx.channel.send("SUCCessfully added.")

    @commands.command(name='uncraigslistme', aliases=["unclemedaddy", "deletequery", "delq"])
    async def uncraigslist_me_daddy(self, ctx, number: int):
        # Deletes craigslist query for user
        queries = db.userget(ctx.author.id, 'clqueries')
        try:
            db.users.update_one(
                {"_id": ctx.author.id},
                {"$pull": {"clqueries": queries[number-1]}}
            )
            return await ctx.channel.send("Query removed.")
        except:
            return await ctx.channel.send("Couldn't remove that query.")

    @commands.command(name='clinfo')
    async def my_queries(self, ctx):
        queries = db.userget(ctx.author.id, 'clqueries')
        if not queries:
            return await ctx.channel.send("You don't have any queries")
        
        current_queries = ""
        for i, query in enumerate(queries):
            current_queries = f"""{current_queries}{i+1}. "{', '.join(query['keywords'])}" | Max Price: ${query['max_price']} | Ping: {bool(query['ping'])}\n"""

        embed=discord.Embed(title=f"Craigslisting for {ctx.author.nick}",
                            description=f"{ctx.author.mention}\n\n{current_queries}",
                            color=discord.Color.blue())
        return await ctx.channel.send(embed=embed)

    async def loop(self):
        while True:
            users = db.users.find({})
            for user in users:
                _id = user['_id']
                zip_code = user['zipcode']
                site = user['site']
                if not site or not zip_code:
                    continue
                
                queries = user['clqueries']
                for query in queries:
                    channel = self.bot.get_channel(query['channel'])
                    listings = self.search(site, zip_code, query, _id)
                    if not listings:
                        print("Nothing new")
                        continue
                    if query['ping']:
                        user = self.bot.get_user(query['ping'])
                        await channel.send(f"{user.mention}, here are some new listings for {', '.join(query['keywords'])}.")
                    for listing in listings:
                        await self.send_listing(listing, channel)
            print("Done searching")
            await asyncio.sleep(60*5)

    def search(self, site, zip_code, query, user_id):
        listings = []  # List to store results of search
        query_id = query['_id']
        # Searches CL with the parameters
        for keyword in query['keywords']:
            print("Searching...")
            generator = CraigslistForSale(
                site=site,
                filters={
                    'query': keyword,
                    'max_price': query['max_price'],
                    'posted_today': True,
                    'bundle_duplicates': True,
                    'has_image': query['has_image'],
                    'search_titles': False,
                    'zip_code': zip_code,
                    'search_distance': query['distance'],
                }
            )
            # Adds listings to a list, include details returns an error if listing doesn't have body
            try:
                for listing in generator.get_results(sort_by='newest', include_details=True):
                    listings.append(listing)
            except:
                for listing in generator.get_results(sort_by='newest'):
                    listings.append(listing)

        listings = self.clean_list(user_id, query_id, query['sent_listings'], listings)
        return listings
    
    def clean_list(self, user_id, query_id, sent_listings, new_listings):
        if not new_listings:
            return None
        clean_listings = []
        updated_list = sent_listings
        for listing in new_listings:
            if listing['id'] not in sent_listings:
                clean_listings.append(listing)
                updated_list.append(listing['id'])
                db.users.update_one(
                    {"_id": user_id, "clqueries._id": query_id},
                    {"$set": {"clqueries.$.sent_listings": updated_list}}
                )

        return clean_listings

    async def send_listing(self, listing, channel):
        print("Preparing to send")
        if 'body' in listing.keys():
            try:
                body = [sentence for sentence in listing['body'].split(
                    '\n') if 'http' not in sentence and len(sentence) > 2]
                body = '\n'.join(body)
            except:
                body = listing['body']
            if len(body) > 350:
                body = f"{body[0:350]}..."
            color = discord.Color.green()
        else:
            body = "Couldn't get details; post was probably deleted."
            color = discord.Color.red()

        embed=discord.Embed(title=f"{listing['price']}, {listing['name']}",
                            description=f"{body}\n\n[Link to Craigslist Post]({listing['url']})",
                            color=color)
        return await channel.send(embed=embed)
    
    def id_maker(self):
        date = datetime.datetime.now()
        count = self.count
        self.count += 1
        return int(f"{date.day}{date.month}{date.year}{count}")

def setup(bot):
    bot.add_cog(Craigslister(bot))