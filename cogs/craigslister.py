"""CRAIGSLISTER"""

import requests

import common.database as db
import discord
from common.cfg import spam_words
try:
    from craigslist import CraigslistForSale
except:
    print("Craigslist sucks dick")

from discord.ext import commands, tasks
from discord.ext.commands import CommandError


class Craigslister(commands.Cog):
    """Hold and executes all craigslisting commands."""
    MAX_QUERIES = 3
    MAX_KEYWORDS = 5

    def __init__(self, bot):
        self.bot = bot
        self.lookup_queries.start()

    def cog_check(self, ctx):
        if not db.users.find_one({"_id": ctx.author.id}):
            data = {
                "_id": ctx.author.id,
                "zipcode": None,
                "site": None,
            }
            db.users.insert_one(data)
        return True

    @commands.command(name="clqr")
    async def cl_quick_reference(self, ctx):
        """Shows query format"""
        return await ctx.send("!clme\nyour, keywords\nprice\ndistance\nimage?\nping?\ncategory?")

    # Setup Commands

    @commands.command(name="setzip", aliases=["zip", "zipcode", "setzipcode"])
    async def set_user_zip(self, ctx, zipcode: int):
        """Updates a user's zip code"""
        db.users.update_one(
            {"_id": ctx.author.id},
            {"$set": {"zipcode": zipcode}}
        )
        return await ctx.send(f"Zip updated to: `{zipcode}`")

    @commands.command(name="setsite", aliases=["site"])
    async def set_user_site(self, ctx, site):
        """Updates a user's CL site"""
        db.users.update_one(
            {"_id": ctx.author.id},
            {"$set": {"site": site}}
        )
        return await ctx.send(f"Site updated to: `{site}`")

    @commands.command(name='craigslistme', aliases=["clme", "addquery", "addq", "clmedaddy"])
    async def craigslist_me_daddy(self, ctx, *, query):
        """Adds a craigslist query"""
        zipcode, site = db.userget_many(ctx.author.id, "site", "zipcode")

        if not site or not zipcode:
            raise CommandError(
                "Please set your site and zipcode using the `setzip` and `setsite` commands")

        if db.queries.count({"owner": ctx.author.id}) >= self.MAX_QUERIES:
            raise CommandError(
                f"You can only have {self.MAX_QUERIES} queries at once.")

        args = query.split("\n")

        # clean values and convert to proper types
        try:
            keywords, budget, dist = args[:3]
            args += ["", "", ""]  # ensure list includes all fields
        except ValueError:
            raise CommandError("Must include at least 3 values")

        keywords = keywords.replace(", ", ",").split(",")
        if len(keywords) > self.MAX_KEYWORDS:
            raise CommandError(f"Max Keywords is {self.MAX_KEYWORDS}")

        # The document that will represent a complete query
        final_query = {
            "owner": ctx.author.id,
            "channel": ctx.channel.id,
            "site": site,
            "zipcode": zipcode,
            "keywords": keywords,
            "listings": []
        }

        try:
            final_query["budget"] = abs(int(budget))
            final_query["distance"] = abs(int(dist))
        except ValueError:
            raise CommandError("Budget/Distance must be a number")

        final_query["has_image"] = bool(args[3])
        final_query["ping"] = bool(args[4])
        final_query["category"] = args[5] if args[5] else "sss"

        # Updates DB
        response = db.queries.insert_one(final_query)
        db.users.update_one(
            {"_id": ctx.author.id},
            {"$push": {"queries": response.inserted_id}}
        )

        return await ctx.channel.send("SUCCessfully added.")

    @commands.command(name='uncraigslistme', aliases=["unclmedaddy", "delq", "unclme"])
    async def uncraigslist_me_daddy(self, ctx, index: int):
        """Deletes specified craigslist query"""
        queries = db.queries.find({"owner": ctx.author.id})
        try:
            db.queries.delete_one(queries[index-1])
        except IndexError:
            raise CommandError("You fucked it, try again")
        await ctx.channel.send("Query removed.")

    @commands.command(name='queries', aliases=["clinfo", "craigslistings"])
    async def show_queries(self, ctx):
        """Displays active queries for user."""
        queries = db.queries.find({"owner": ctx.author.id})

        query_embed = discord.Embed(
            title=f"Craigslistings for {ctx.author.name}",
            color=discord.Color.blue()
        )
        query_embed.set_footer(
            text="If this looks empty its because you aint craigslisting")

        # populate the embed with data
        for i, query in enumerate(queries, 1):
            query_embed.add_field(
                name=f"{i}. {', '.join(query['keywords'])}",
                value=f"Budget: ${query['budget']}\nPing: {bool(query['ping'])}",
                inline=False
            )

        await ctx.send(embed=query_embed)

    @tasks.loop(seconds=300)
    async def lookup_queries(self):
        """Searches CL every 5 minutes for every query that every user has"""
        queries = db.queries.find({})

        for query in queries:
            listings = self.search(query)  # fetch all listings

            # update database with last listing result
            listing_ids = [listing["id"] for listing in listings]
            db.queries.update_one(
                {"_id": query["_id"]},
                {"$set": {"listings": listing_ids}}
            )

            # send only new listings
            new_listings = [l for l in listings if l["id"]
                            not in query["listings"]]
            new_listings = self.spam_filter(new_listings, query['keywords'])
            if not new_listings:
                continue

            channel = self.bot.get_channel(query["channel"])

            # Ping if user requested ping
            if query['ping']:
                user = self.bot.get_user(query['owner'])
                await channel.send(f"{user.mention}, here are some new listings for {', '.join(query['keywords'])}.")

            # Send it
            for listing in new_listings:
                await self.send_listing(listing, channel)

    @lookup_queries.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @staticmethod
    def search(query):
        """Uses the query to search CL. 
        Returns a list of ALL matching posts"""

        listings = []

        # Iterate through keywords and search CL
        for keyword in query['keywords']:
            # Searches CL with the parameters
            generator = CraigslistForSale(
                site=query["site"],
                category=query['category'],
                filters={
                    'query': keyword,
                    'max_price': query['budget'],
                    'posted_today': True,
                    'bundle_duplicates': True,
                    'has_image': query['has_image'],
                    'search_titles': False,
                    'zip_code': query["zipcode"],
                    'search_distance': query['distance'],
                }
            )

            # Adds listings to a list, include details returns an error if listing doesn't have body
            try:
                for listing in generator.get_results(sort_by='newest', include_details=True):
                    listings.append(listing)
            except requests.exceptions.HTTPError:
                for listing in generator.get_results(sort_by='newest'):
                    listings.append(listing)

        return listings

    @staticmethod
    def spam_filter(listings, keywords):
        clean_listings = []
        for listing in listings:

            # Check if body exists in listing
            if 'body' in listing.keys():
                try:
                    # Removes links and short sentences from the body
                    body = [sentence for sentence in listing['body'].split(
                            '\n') if 'http' not in sentence and len(sentence) > 2]
                    body = '\n'.join(body)
                except:
                    pass
                finally:
                    listing['body'] = body
            else:
                # No body, post was probably deleted, skip spam check
                listing['body'] = "Couldn't get details; post was probably deleted."
                clean_listings.append(listing)
                continue

            spam = 0
            if len(body) > 500:
                # remove keywords from spam list
                spam_wrds = [i for i in [e.upper() for e in spam_words] if i not in [
                    j.upper() for j in keywords]]
                for word in spam_wrds:
                    # -1 means the word is not found
                    if body.find(word) != -1:
                        spam += 1
                    # Too spammy so break
                    if spam > 1:
                        break

            # If less than 2 strikes then add to list
            if spam < 2:
                clean_listings.append(listing)

        return clean_listings

    async def send_listing(self, listing, channel):
        """Takes a listing object and sends it to the specified channel"""

        display_limit = 350

        # If the body is longer than the display limit, only show the max amount of characters
        body = listing['body']
        if len(body) > display_limit:
            body = f"{body[0:display_limit]}..."

        # Formats and sends the embed
        embed = discord.Embed(title=f"{listing['price']}, {listing['name']}",
                              description=f"{body}\n\n[Link to Craigslist Post]({listing['url']})",
                              color=discord.Color.blue())
        return await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Craigslister(bot))
