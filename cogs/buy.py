import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
import time

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


class buy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("buy cog is online.")

    @commands.command()
    async def buy(self,ctx, item=None, amount=1):

        user_bal = database.child("users").child(ctx.author.id).child("currency").get().val()

        if item == None:
            await ctx.reply("Please specify the item.")

        elif item.lower() == "pulls" or item.lower() == "pull":
            if amount != 0:
                if user_bal >= amount*10:
                    database.child("users").child(ctx.author.id).update({"currency": user_bal-(amount*10)})
                    current_pulls = database.child("users").child(ctx.author.id).child("pulls").child("amount").get().val()
                    database.child("users").child(ctx.author.id).child("pulls").update({"amount": current_pulls+amount})
                    await ctx.reply(f"added {amount} pulls to your account.")
                    # else:
                    #   await ctx.reply("You don't have enough money.")


        elif item.lower() == "claims" or item.lower() == "claim":
            current_unix = int(time.time())
            user_unix = database.child("users").child(ctx.author.id).child("claim_time").get().val()

        if current_unix > user_unix:
            await ctx.reply("You can claim right now. Buying this is useless.")

        elif current_unix < user_unix:

            if user_bal > 500 or user_bal == 500:
                new_bal = user_bal - 500
                await ctx.reply(f"Bought Claim Reset. You can now claim a card. Your new balance is {new_bal}")
                database.child("users").child(ctx.author.id).update({"claim_time": 1})
                database.child("users").child(ctx.author.id).update({"currency": new_bal})

            if user_bal < 500:
                await ctx.reply("You don't have enough <:cecilia:1038333000905134141> to buy \"claim\"")
                print(user_bal)
        
async def setup(bot):
    await bot.add_cog(buy(bot))