import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
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


class view(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("view cog is online.")

    @commands.command()
    async def view(self,ctx, *, card=None):
        # try:
        if card == None:
            await ctx.reply("Specify a card!")
        else:
        
            parse_index = card[2:]
            if int(parse_index) >= 10:
                parse_rarity = card[:-3]
            elif int(parse_index) < 10:
                parse_rarity = card[:-2]
    

            card = database.child("cards").child(f"rarity-{parse_rarity}").child(parse_index).get().val()

            if card['rarity'] == 3 or card['rarity'] == "3":
        
                rarity = '⭐⭐⭐'
            elif card['rarity'] == 4 or card['rarity'] == "4":
        
                rarity = '⭐⭐⭐⭐'

            elif card['rarity'] == 5 or card['rarity'] == "5":
                rarity = '⭐⭐⭐⭐⭐'

            embed = discord.Embed(title=f"PREVIEW", description=f"**Art By {card['artist']}**\n**{card['card_name']}**\n{rarity}\n[link]({card['post_link']})", color=discord.Color.random())
            embed.set_image(url=card['image'])

            if card['claimed'] == "true" or card['claimed'] == True:
                uid: int = card['owned_by']
                uid_to_user = await self.bot.fetch_user(uid)
                uid_to_user = str(uid_to_user)[:-5]
                embed.set_footer(text=f"Owned by {uid_to_user}")

            await ctx.reply(embed=embed)
        
        
async def setup(bot):
    await bot.add_cog(view(bot))