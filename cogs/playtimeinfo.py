import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
import asyncio
import genshin
from humanfriendly import format_timespan, parse_timespan
import datetime
from urllib.request import Request, urlopen
import time
import json
from discord import app_commands

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



class ptInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pt_info_menu = app_commands.ContextMenu(
            name='Play time info',
            callback=self.pt_info, # set the callback of the context menu to "my_cool_context_menu"
        )
        self.bot.tree.add_command(self.pt_info_menu, guilds=[discord.Object(id=991361510263767080)])
        

    async def pt_info(self, interaction: discord.Interaction, message: discord.Message):
        try:
            embed = discord.Embed(title="Genshin Play Time Tracker", description="You can now view how much time you've spent playing Genshin Impact.", color=3092790)
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.followup.send("This user is not registered.", ephemeral=True)
            print(e)
        
            

# async def setup(bot):
#     await bot.add_cog(ptInfo(bot))

async def setup(bot):
    await bot.add_cog(ptInfo(bot), guilds=[discord.Object(id=991361510263767080)])