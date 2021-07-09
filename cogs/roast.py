import discord
import random
from discord.ext import commands

class Roasts(commands.Cog):
    #Part of the bot that handles roasting

    def __init__(self, bot):
        self.bot = bot
        self.roasts = {
            "You ugly", "You're an idiot", 
            "You're shittier than FinalMouse"
        }
    
    
    #initalize bot and possible roasts

    @commands.command(name="roast", aliases=['roats'])
    async def roast_member(self, ctx, victim: discord.Member):
        await ctx.send(random.choice(self.roasts))

def setup(bot):
    bot.add_cog(Roasts(bot))









#    if message.content.lower() in cogs.poggers_activation_phrases:
 #           await message.channel.send(random.choice(cfg.poggers_links))
    
