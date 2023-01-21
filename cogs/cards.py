import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
from humanfriendly import format_timespan

load_dotenv()

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


class cards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("cards cog is online.")

    @commands.command()
    async def cards(self,ctx):
        try:
            card_list_data = database.child("users").child(ctx.author.id).child("owned_cards").get()
        
            i = ''
            for card in card_list_data.each():
                if card.val()['Card_rarity'] == "3":
                    rarity = "⭐⭐⭐"
                elif card.val()['Card_rarity'] == "4":
                    rarity = "⭐⭐⭐⭐"
                elif card.val()['Card_rarity'] == "5":
                    rarity = "⭐⭐⭐⭐⭐"

                i += f"\n{rarity} **{card.val()['Card_name']}** ID: {card.val()['Card_ID'][7:]}"
                
            embed = discord.Embed(title=f"{ctx.author.name}'s Cards", description=f"{i}", color=ctx.author.color)
            await ctx.reply(embed=embed)
        
        except:
            await ctx.reply("Babe you haven't claimed any cards yet.")
        
async def setup(bot):
    await bot.add_cog(cards(bot))