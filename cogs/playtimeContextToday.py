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



class ptContext(commands.Cog):
    def __init__(self, bot):
        print("ptcontect")
        self.bot = bot
        self.pt_context = app_commands.ContextMenu(
            name='Play time today',
            callback=self.pt_context_action, # set the callback of the context menu to "my_cool_context_menu"
        )
        self.bot.tree.add_command(self.pt_context, guilds=[discord.Object(id=991361510263767080)])
        

    async def pt_context_action(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer()
        try:
            if database.child("boon").child("playtime").child(message.author.id).child("settings").child("timezone").shallow().get().val():
                user_tz = database.child("boon").child("playtime").child(message.author.id).child("settings").child("timezone").get().val()
                tz = pytz.timezone(user_tz)
                date_now = datetime.datetime.now(tz=tz)
                year = date_now.strftime('%Y')
                month = date_now.strftime("%m")
                day = date_now.strftime("%d")
                date_today = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
                date_today_last = datetime.datetime(int(year), int(month), int(day), 23, 59, 59)
                date_today_unix = int(time.mktime(date_today.timetuple()))
                date_today_last_unix = int(time.mktime(date_today_last.timetuple()))

                sessions_today = database.child("boon").child("playtime").child(message.author.id).child(year).child(month).shallow().get().val()
                durations = []
                session_data = database.child("boon").child("playtime").child(message.author.id).child(year).child(month).get().val()
                for session in sessions_today:
                    if int(session) >= date_today_unix and int(session) <= date_today_last_unix:
                        durations.append(session_data[session]["Duration"])
                if durations:
                    total_duration = sum(durations)
                    humanfriendly = format_timespan(total_duration, max_units=2)
                    embed = discord.Embed(title=f"{message.author.name}'s Genshin play time today", description=f"{humanfriendly}", color=3092790)
                    await interaction.followup.send(embed=embed)
                elif not durations:
                    embed = discord.Embed(title="Error", description=f"{message.author.name} has not played Genshin today.\n\nReminder: This only records your playtime if \"Genshin Impact\" is displayed on your Discord rich presence or **Playing** status. Unfortunately this only works properly if you play on pc.", color=3092790)
                    embed.set_image(url="https://media.discordapp.net/attachments/1008333194271129600/1058764636519927808/image.png")
                    await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{message.author.name} does not have a timezone set", description=("You can use </playtime thismonth:1057666922587639858> or </playtime thisyear:1057666922587639858> instead."), color=3092790)
                await interaction.followup.send(embed = embed)
        except Exception as e:
            print(e)
        
            

# async def setup(bot):
#     await bot.add_cog(ptContext(bot))

async def setup(bot):
    await bot.add_cog(ptContext(bot), guilds=[discord.Object(id=991361510263767080)])