import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
import pyrebase
import random
import string
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


class codeGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("code generator (code) cog is online.")

    @commands.command()
    async def code(self,ctx):
        def get_random_string(length):
            letters = string.ascii_letters
            result_str = ''.join(random.choice(letters) for i in range(length))
            return(result_str)
        
        token = get_random_string(50)
        await ctx.reply(token)
        user = ctx.author.name
        database.child('with_token').update({ctx.author.id: True})
        database.child('authtokens').update({token: {"uid": str(ctx.author.id), "username": user}})
        

        
async def setup(bot):
    await bot.add_cog(codeGen(bot))