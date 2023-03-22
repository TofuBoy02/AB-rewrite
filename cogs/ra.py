import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
from humanfriendly import format_timespan
import genshin
import asyncio

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


class redeemall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("redeem all (ra) cog is online.")

    @commands.command()
    async def ra(self,ctx, rcode):
        try:
            users = database.child('boon').child('notes').child('users').get().val()
            for user in users:
                await asyncio.sleep(0.5)
                try:
                    uid_to_user = self.bot.get_user(int(user))
                    if 'cookie_token' in users[user].keys():
                        try:
                            print(users[user]['cookie_token'])
                            uid = users[user]['uid']
                            cookie_token = users[user]['cookie_token']
                            ltoken = users[user]['ltoken']
                            ltuid = users[user]['ltuid']
                            gc = genshin.Client({'cookie_token': cookie_token, 'ltoken': ltoken, 'uid': uid, 'account_id': ltuid})
                            # gc.set_cookies({'account_id': uid, 'cookie_token': cookie_token, 'ltoken': ltoken, 'ltuid': ltuid})
                            await gc.redeem_code(code=rcode, uid=uid)
                            
                            await ctx.send(f'Successfully redeemed {rcode} for {uid_to_user}')

                        except Exception as e:

                            await ctx.send(f'Could not redeem code for {uid_to_user} {user}:\n`{e}`')
                except Exception as e:
                    print(e)

        
        except Exception as e:
            print(f"ERROR: {e}")
        
async def setup(bot):
    await bot.add_cog(redeemall(bot))