import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
import asyncio
import genshin

TOKEN = os.getenv('TOKEN')


service = {
    
  "type": "service_account",
  "project_id": os.getenv('project_id'),
  "private_key_id": os.getenv('private_key_id'),
  "private_key": os.getenv('private_key'),
  "client_email": os.getenv('client_email'),
  "client_id": os.getenv('client_id'),
  "auth_uri": os.getenv('auth_uri'),
  "token_uri": os.getenv('token_uri'),
  "auth_provider_x509_cert_url": os.getenv('auth_provider_x509_cert_url'),
  "client_x509_cert_url": os.getenv('client_x509_cert_url')
}

config = {
    'apiKey': os.getenv('apiKey'),
    'authDomain': os.getenv('authDomain'),
    'projectId': os.getenv('projectId'),
    'storageBucket': os.getenv('storageBucket'),
    'messagingSenderId': os.getenv('messagingSenderId'),
    'appId': os.getenv('appId'),
    'measurementId': os.getenv('measurementId'),
    'databaseURL': os.getenv('databaseURL'),
    "serviceAccount": service

} 

firebase = pyrebase.initialize_app(config)
database = firebase.database()

class gaclaim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("gaclaim cog is online.")

    @commands.command()
    async def gaclaim(self,ctx):
        try:
            users = database.child("boon").child("notes").child("users").shallow().get().val()
            duplicates = [756246647377232043, 810322903820271617]
            for user in users:
                if user not in duplicates:
                    username = await self.bot.fetch_user(user)
                    user_data = database.child("boon").child("notes").child("users").child(user).get().val()
                    ltoken = user_data["ltoken"]
                    ltuid = user_data["ltuid"]
                    uid = user_data["uid"]
                    gc = genshin.Client({"ltuid": ltuid, "ltoken": ltoken})
                    gc.default_game = genshin.Game.GENSHIN
                    try:
                        reward = await gc.claim_daily_reward()
                    except genshin.AlreadyClaimed:
                        await ctx.send(f"<:tick:772044532845772810> Daily reward already claimed for {username}")
                    except genshin.AuthkeyException as e:
                        await ctx.send(f"<:cross:772100763659927632> Could not claim {username}'s account.\n`{e}`")
                    except Exception as e:
                        await ctx.send(f"<:cross:772100763659927632> For {username}: `{e}`")
                    else:
                        await ctx.send(f"<:tick:772044532845772810> Claimed {reward.amount}x {reward.name} for {username}")
                    await asyncio.sleep(1)
                    if "alts" in user_data:
                        try:
                            await ctx.send(f"<:WL:1036184269950820422> Alt accounts for {username} detected. Claiming rewards for all alts.")
                            for alts in user_data["alts"]:
                                alt_ltoken = (user_data["alts"][alts]["ltoken"])
                                alt_ltuid = (user_data["alts"][alts]["ltuid"])
                                alt_uid = (user_data["alts"][alts]["uid"])
                                gc = genshin.Client({"ltuid": alt_ltuid, "ltoken": alt_ltoken})
                                gc.default_game = genshin.Game.GENSHIN
                                try:
                                    reward = await gc.claim_daily_reward()
                                except genshin.AlreadyClaimed:
                                    await ctx.send(f"<:tick:772044532845772810> Daily reward already claimed for {username}'s Alt account: {alts}")
                                except genshin.AuthkeyException as e:
                                    await ctx.send(f"<:cross:772100763659927632> Could not claim {username}'s Alt account: {alts}\n`{e}`")
                                except Exception as e:
                                    await ctx.send(f"<:cross:772100763659927632> For {username}: `{e}`")
                                else:
                                    await ctx.send(f"<:tick:772044532845772810> Claimed {reward.amount}x {reward.name} for {username}'s Alt account: {alts}")
                                await asyncio.sleep(1)
                        except Exception as e:
                            await ctx.send(f"Error: `{e}`")
        except Exception as e:
            await ctx.send(f"Error: `{e}`")    
                
            
async def setup(bot):
    await bot.add_cog(gaclaim(bot))
