import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
import time
import datetime
from datetime import date
from datetime import timezone
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

class genshinTime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Genshin time is online.")


    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.guild.id == 991361510263767080:
            try:
                if before.activity.name == "Genshin Impact":
                    print(before.activity.name)
                    current_time = int(time.time())
                    time_started = before.activity.timestamps["start"]//1000
                    year = datetime.datetime.utcfromtimestamp(time_started).strftime('%Y')
                    month = datetime.datetime.utcfromtimestamp(time_started).strftime('%m')
                    
                    duration = current_time - time_started
                    data = {"Started": time_started, "Ended": current_time, "Duration": duration}
                    database.child("boon").child("playtime").child(before.id).child(year).child(month).child(time_started).update(data)


            except Exception as e:
                print(e)

async def setup(bot):
    await bot.add_cog(genshinTime(bot))