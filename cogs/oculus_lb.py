import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
from humanfriendly import format_timespan
from collections import OrderedDict

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


class oculuslb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("oculus lb cog is online.")


    @commands.command()
    async def oclb(self,ctx):
        try:
            data = database.child("boon").child("notes").child("lb").get().val()
            sorted_data = OrderedDict(sorted(data.items(), key=lambda x: x[1]['total'], reverse=True))
            users = ''
            rank = 1
            for user in sorted_data:
                users += (f"#{rank}: <@{user}> ({data[user]['total']}) \n")
                rank += 1
            
            
            embed = discord.Embed(title="<:dendroculus:1037646414689345537> Oculus Leaderboard", description=f"{users}\n\n*Data is indexed every 10 hours*\nUpdate yours using `.n`", color=3092790)
            await ctx.reply(embed=embed)

                
        except Exception as e:
            await ctx.reply(f"An error occured.\n`{e}`")
        
        
async def setup(bot):
    await bot.add_cog(oculuslb(bot))