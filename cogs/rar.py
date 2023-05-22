import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
TOKEN = os.getenv('TOKEN')



class rar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ra cookie reminder cog is online.")

    @commands.command()
    async def rar(self,ctx):
        accounts = [305711404747587585, 437745619684032512, 459655669889630209, 910432700421259274, 947526371041763389]
        # accounts = [459655669889630209]
        if ctx.author.id == 459655669889630209:

            for account in accounts:
                username = await self.bot.fetch_user(account)
                print(str(username)[:-5])
                embed = discord.Embed(title="Auto Redeem Code Cookie", description=f"Hi {str(username)[:-5]},\n\nPlease update your cookie token by doing </register:1059412154610106458>. Since your cookies are expired, I cannot redeem codes automatically for you.\n\nCookie Token is only for redemption codes, you can still check your live notes without udpating your Cookie Token.", color=14428490)
                await username.send(embed=embed)
                await ctx.send(f'Sent dm to {username} {account}')
        else:
            await ctx.reply("You don't have permission to use this command.")
            

        
async def setup(bot):
    await bot.add_cog(rar(bot))