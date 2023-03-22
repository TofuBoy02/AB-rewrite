import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
TOKEN = os.getenv('TOKEN')



class announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ann cog is online.")

    @commands.command()
    async def ann(self,ctx, channelp, title, desc, footer):
        try:
            channel = self.bot.get_channel(int(channelp))
            embed = discord.Embed(title=title, color=16305198, description=desc)
            embed.set_footer(text=footer)
            await channel.send(embed=embed)
            await ctx.reply(f"Embed sent to <#{channelp}>")
        except Exception as e:
            print(e)

        
async def setup(bot):
    await bot.add_cog(announce(bot))