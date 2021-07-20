"""Facilitates a game of hangman via Discord."""

import asyncio
from typing import Optional
import discord
from discord.ext import commands
from discord.ext.commands import UserInputError
from pymongo import ReturnDocument

import common.database as db


class Hangman(commands.Cog):
    """Handles all commands and listeners for hangman."""

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def hidden_string(phrase, guessed):
        """Return string with missing letters in hangman."""
        word = " ".join(
            ["\_" if c.isalpha() and c not in guessed else c for c in phrase])
        return word + f"    Wrong Answers: {', '.join([c.upper() for c in guessed if c not in phrase])}"

    @commands.command(name="hangman")
    async def start_hangman(self, ctx, channel: Optional[discord.TextChannel], players: commands.Greedy[discord.Member]):
        """Begins the game of hangman and DM command author for mystery word."""
        # flag channel for deletion if channel was created by bot
        dedicated_channel = not channel
        everyone_in = not players  # everyone in if no members provided

        # Everyone can play if not specified
        if everyone_in:
            players = ctx.guild.members

        # Add game to database
        db.hangman.insert_one(
            {
                "_id": ctx.author.id,
                "word": None,
                "channel": None if dedicated_channel else channel.id,
                "dedicated": dedicated_channel,
                "players": [p.id for p in players],
                "guessed": []
            }
        )

        # create dedicated channel if needed
        if dedicated_channel:
            channel = await ctx.guild.create_text_channel(f"{ctx.author.name}-hangman")
            db.hangman.update_one(
                {"_id": ctx.author.id},
                {"$set": {"channel": channel.id}},
            )

        # DM author asking for a mystery word
        embed = discord.Embed(
            title="Please enter a word/phrase for hangman",
            description="Mystery Word: ",
        )
        embed.add_field(
            name="Players",
            value="Anyone" if everyone_in else "\n".join([str(p) for p in players]))
        embed.add_field(name="Channel", value=channel.name)
        await ctx.author.send(embed=embed)

    @commands.command(name="endhangman")
    async def end_hangman(self, ctx):
        """Ends the authors current game of hangman."""
        deleted_data = db.hangman.find_one_and_delete(
            {"_id": ctx.author.id}, {"_id": 0, "channel": 1, "dedicated": 1}
        )

        # inform user if game was deleted or not
        if deleted_data:
            channel = ctx.guild.get_channel(deleted_data["channel"])

            # inform user that game is over
            if channel.id == ctx.channel.id:
                await ctx.author.send("Your game has been endedd")
            else:
                await ctx.send("Your game has been ended")

            # deleted dedicated channel if exists
            if deleted_data["dedicated"]:
                await channel.delete()
        else:
            await ctx.send(f"You have no active games")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id:
            return

        # message may be a starting word
        if isinstance(message.channel, discord.DMChannel):
            # Minimum of 3 guessable letters for mystery word
            if sum(char.isalpha() for char in message.content) < 3:
                return await message.channel.send("Cmon bro, at least 3 letters")

            # Add word to database and allow guessing
            data = db.hangman.find_one_and_update(
                {"_id": message.author.id, "word": None},
                {"$set": {"word": message.content.lower()}},
                {"_id": 0, "channel": 1},
            )

            channel = self.bot.get_channel(data["channel"])
            return await channel.send(
                f"{message.author.mention}'s Hangman Game\n{self.hidden_string(message.content.lower(), [])}"
            )

        # messages must be single letters to qualify as a guess
        if message.content.isalpha() and len(message.content) == 1:
            game_data = db.hangman.find_one_and_update(
                {
                    "channel": message.channel.id,
                    "word": {"$ne": None},
                    "players": message.author.id,
                },
                {"$addToSet": {"guessed": message.content.lower()}},
                return_document=ReturnDocument.AFTER,
            )
            # message is not related to game
            if not game_data:
                return

            # set of letters that are in the mystery word
            valid_letters = {c for c in game_data["word"] if c.isalpha()}
            word_data = (game_data["word"], game_data["guessed"])

            # Players won the game
            if not valid_letters - set(game_data["guessed"]):
                victory_embed = discord.Embed(
                    title="Players Guessed The Word",
                    description=f"The word was: {game_data['word']}",
                    color=discord.Color.green()
                )
                await message.channel.send(embed=victory_embed)
                db.hangman.delete_one({"_id": game_data["_id"]})  # remove game

                # remove dedicated channel
                if game_data["dedicated"]:
                    await message.channel.send("This channel will be deleted momentarily.")
                    await asyncio.sleep(10)
                    await message.channel.delete()
            else:
                if len(set(game_data["guessed"]) - valid_letters) < 6:
                    await message.channel.send(self.hidden_string(*word_data))
                else:
                    # Players lose
                    loss_embed = discord.Embed(
                        title="Players did not guess the word",
                        description=f"The word was: {game_data['word']}",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=loss_embed)
                    db.hangman.delete_one({"_id": game_data["_id"]})

                    # remove dedicated channel
                    if game_data["dedicated"]:
                        await message.channel.send("This channel will be deleted momentarily.")
                        await asyncio.sleep(60)
                        await message.channel.delete()


def setup(bot):
    bot.add_cog(Hangman(bot))
