"""Allows for a DM if a command is not well-suited for user input."""

# TODO COMMENTS

import random
import discord
from discord.ext import commands
from discord.ext.commands.core import check
from common.cfg import builders

checkmark = "✅"
crossmark = "❌"


class QueryBuilderListeners(commands.Cog):
    """Handles and builds complex queries in a DM"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Responds to reactions."""
        try:
            # ignore bot or non-related reaction
            if user.id == self.bot.user.id or user.dm_channel.id != reaction.message.channel.id:
                return
            builder = builders[user.id]
        except (KeyError, AttributeError):
            return

        typefn = builder.instructions[builder.current_field]['type']
        if typefn not in (bool, list) or builder.msg.id != reaction.message.id:
            return

        if reaction.emoji == checkmark:
            if builder.finalizing:
                builder.fn(builder.form)  # Send data to finishing fn
                del builders[user.id]  # remove active session
                return await user.send("Good shit brother. You good to go now")

            # Ensure keywords in list
            if typefn == list:
                try:
                    _ = builder.form[builder.current_field]
                    return await builder.next_field()
                except KeyError:
                    return await user.send("You didn't even fucking add a keyword. How the fuck am I supposed to find sick deals with no keywords.")

            builder.form[builder.current_field] = True
            await builder.next_field()

        elif reaction.emoji == crossmark:
            if builder.finalizing:
                del builders[user.id]
                return await user.send("I'll never forgive you for wasting my time like this. Get the fuck outta my DMs")

            if typefn == list:
                return

            builder.form[builder.current_field] = False
            await builder.next_field()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Responds to messages"""
        user = message.author
        try:
            # ignore bot or non-related reaction
            if user.id == self.bot.user.id or user.dm_channel.id != message.channel.id:
                return
            builder = builders[message.author.id]
        except (KeyError, AttributeError):
            return

        if builder.finalizing:
            return

        typefn = builder.instructions[builder.current_field]['type']
        if typefn == bool:
            return await user.send("Delete that shit right now and click one of the reactions", delete_after=5.0)

        if typefn == list:
            try:
                builder.form[builder.current_field] += [message.content]
            except KeyError:
                builder.form[builder.current_field] = [message.content]
            return

        try:
            builder.form[builder.current_field] = typefn(message.content)
            await builder.next_field()
        except ValueError:
            return await message.channel.send(
                f"U gotta be shitting me. The field needs to be of type `{typefn.__name__}` you god damn troglodyte.",
                delete_after=5.0
            )


def setup(bot):
    bot.add_cog(QueryBuilderListeners(bot))


class QueryBuilder:

    words_of_encouragement = [
        "You got this bro. The whole squad rooting for you <3",
        "You're shining like a diamond right now :)",
        "On god I wish my brain was as wrinkled as yours",
        "Watching you fill out this form gives me hope for humanity",
        "You're going sicko mode on this form right now",
        "If perfection had a name it would be GumBOTchi, But you're a close second"
    ]

    def __init__(self, user, instructions, fn):
        """
        Base class for any paginated message
        form should be a basic dict with fields and values

        Instructions should be formatted with keys that match the form
        Each key for instructions should contain a dict with a key "text" which
        is the instruction and a key "type" which should be a type class such as int or bool

        The fn argument should be a function that takes the filled out form as a parameter
        """
        self.form = {}
        self.user = user
        self.key_iter = iter(instructions.keys())  # iterate over fields
        self.current_field = next(self.key_iter)
        self.instructions = instructions
        self.fn = fn
        self.msg = None
        self.finalizing = False
        builders[user.id] = self  # add to builder pool

    def generate_embed(self):
        form_embed = discord.Embed(
            title=f"{self.instructions[self.current_field]['text']}")
        form_embed.set_footer(text=random.choice(self.words_of_encouragement))
        return form_embed

    async def add_reactions(self):
        await self.msg.add_reaction(checkmark)
        await self.msg.add_reaction(crossmark)

    async def start(self):
        """Sends the message containing the form to be filled out"""

        start_embed = discord.Embed(
            title="Build-A-Query",
            description="Just follow the directions."
        )
        await self.user.send(embed=start_embed)

        self.msg = await self.user.send(embed=self.generate_embed())
        if self.instructions[self.current_field]['type'] in (bool, list):
            await self.add_reactions()

    async def next_field(self):
        """Updates prompt with next field and instructions"""
        try:
            self.current_field = next(self.key_iter)
        except StopIteration:
            return await self.finalize()

        await self.msg.delete()
        self.msg = await self.user.send(embed=self.generate_embed())
        typefn = self.instructions[self.current_field]['type']
        if typefn in (bool, list):
            await self.add_reactions()

    async def finalize(self):
        self.finalizing = True
        final_embed = discord.Embed(
            title=f"And then everyone clapped",
            description="Click ✅ to SEND IT or Click ❌ to out yourself as a dumbass"
        )
        formstring = "\n".join([f"{k}: {v}" for k, v in self.form.items()])
        final_embed.add_field(name="Ya Query", value=formstring)

        await self.msg.delete()
        self.msg = await self.user.send(embed=final_embed)
        await self.add_reactions()
