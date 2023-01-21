import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.getenv('TOKEN')

class claimreminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("claimreminder cog is online.")

    @commands.command()
    async def claim(self,ctx):
        await ctx.reply("React to the card with any emoji to claim a card.")
  
async def setup(bot):
    await bot.add_cog(claimreminder(bot))