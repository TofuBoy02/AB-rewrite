import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
import pyrebase
TOKEN = os.getenv('TOKEN')
import time

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


class pulladd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loopadd.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("pulladd cog is online.")

    @tasks.loop(minutes=10)
    async def loopadd(self):
        print("looping")
        database.child("pull_refresh").child("unix").set(int(time.time()) + 600)
        all_users = database.child("users").shallow().get().val()
        # print(all_users)
        for user in all_users:
            # print(user)
            if database.child("users").child(user).child("pulls").get().val():
                user_data = database.child("users").child(user).child("pulls").get().val()
                # print(user_data)
                max_pulls = user_data['max']
                current_pulls = user_data['amount']
                speed = user_data['speed']

                
                if current_pulls + speed <= max_pulls:
                    database.child("users").child(user).child("pulls").update({"amount": current_pulls + speed})
                    # print("added because current pulls + speed is lesser or equal to maximum")
                # elif current_pulls >= max_pulls:
                    # print("do nothing because user has more pulls rn")
                elif current_pulls < max_pulls and current_pulls + speed > max_pulls:
                    database.child("users").child(user).child("pulls").update({"amount": max_pulls})
                    # print("Adding speed will result in overflow, but not adding will leave user with incomplete inventory, so set the pull count to max instead.")
                else:
                    pass
                    # print("what")


            # print("************")
        

    @loopadd.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()
        
async def setup(bot):
    await bot.add_cog(pulladd(bot))