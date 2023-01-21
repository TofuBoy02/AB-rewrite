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


class pulls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("pulls cog is online.")

    @commands.command()
    async def pulls(self,ctx):
        try:
            pulls = database.child("users").child(ctx.author.id).child("pulls").child("amount").get().val()
            if pulls == None:
                await ctx.reply("You need to pull first to initiate an account.")
                return
            await ctx.reply(f"You have {pulls} pulls.")
        except:
            await ctx.reply("Your account is not listed in the database! You should pull first.")
        
        
async def setup(bot):
    await bot.add_cog(pulls(bot))