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

class give(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("give cog is online.")

    @commands.command()
    async def give(self,ctx, user=None, amount=None):
    
        try:
    
            if user != None:
                if user.startswith("<@"):
                    user = int(user[2:-1])
                    uid_to_user = self.bot.get_user(user).name
            else:
                uid_to_user = self.bot.get_user(int(user)).name
                current = database.child("users").child(user).child("currency").get().val()
                database.child("users").child(user).update({"currency": current + int(amount)})
            
            await ctx.reply(f"Added {amount} cecilias to {uid_to_user}")
        except Exception as e:
            print(e)
            await ctx.reply(f"Error: {e}")
            return
  
async def setup(bot):
    await bot.add_cog(give(bot))