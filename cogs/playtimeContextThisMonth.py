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
import pytz

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



class ptContextMonth(commands.Cog):
    def __init__(self, bot):
        print("ptcontectmonth")
        self.bot = bot
        self.pt_context_month = app_commands.ContextMenu(
            name='Play time this month',
            callback=self.pt_context_month_action, # set the callback of the context menu to "my_cool_context_menu"
        )
        self.bot.tree.add_command(self.pt_context_month, guilds=[discord.Object(id=991361510263767080)])
        

    async def pt_context_month_action(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer()
        try:
            year = datetime.datetime.now().strftime('%Y')
            month = datetime.datetime.now().strftime("%m")
            day = datetime.datetime.now().strftime("%d")
            try:
                sessions_this_month = database.child("boon").child("playtime").child(message.author.id).child(year).child(month).get().val()
                durations = []
                for session in sessions_this_month:
                    durations.append(sessions_this_month[session]["Duration"])
                total_duration = sum(durations)
                humanfriendly = format_timespan(total_duration, max_units=2)
                embed = discord.Embed(title=f"{message.author.name}'s Genshin play time this month", description=f"{humanfriendly}", color=3092790)
                await interaction.followup.send(embed=embed)
            except Exception as e:
                print(e)
                embed = discord.Embed(title="Error", description=f"{message.author.name} has not played Genshin this month. Keep it up!\n\nReminder: This only records your playtime if \"Genshin Impact\" is displayed on your Discord rich presence or **Playing** status. Unfortunately this only works properly if you play on pc.", color=3092790)
                embed.set_image(url="https://media.discordapp.net/attachments/1008333194271129600/1058764636519927808/image.png")
                await interaction.followup.send(embed=embed)

        except Exception as e:
            print(e)
        
            

# async def setup(bot):
#     await bot.add_cog(ptContextMonth(bot))

async def setup(bot):
    await bot.add_cog(ptContextMonth(bot), guilds=[discord.Object(id=991361510263767080)])