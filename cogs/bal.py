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


class bal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("bal cog is online.")

    @commands.command()
    async def bal(self,ctx, user=None):
        if user == None:
            try:
                balance = database.child("users").child(ctx.author.id).child("currency").get().val()
                await ctx.reply(f"You have {balance} <:cecilia:1038333000905134141>")
            except:
                await ctx.reply("You have no cecilias! You can earn cecilias by claiming cecilia cards or selling your claimed cards!")
        elif user != None:
            try:
                if user.startswith("<@"):
                    user = int(user[2:-1])
                    uid_to_user = self.bot.get_user(user).name
                else:
                    uid_to_user = self.bot.get_user(int(user)).name
                    balance = database.child("users").child(user).child("currency").get().val()
                    await ctx.reply(f"{uid_to_user} have {balance} <:cecilia:1038333000905134141>")
            except:
                await ctx.reply("Could find {uid_to_user}'s account.")
        
async def setup(bot):
    await bot.add_cog(bal(bot))