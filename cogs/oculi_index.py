import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
import pyrebase
TOKEN = os.getenv('TOKEN')
import time
import genshin

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
        self.oculi_update.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("oculi index cog is online.")

    @tasks.loop(hours = 10)
    async def oculi_update(self):
        print("Updating oculi index")
        def get_all_user():
            data = database.child("boon").child("notes").child("users").get().val()
            return data

        all_users = get_all_user()

        def get_user_ltoken(id, data):
            ltoken = data[id]["ltoken"]
            return ltoken

        def get_user_ltuid(id, data):
            ltuid = data[id]["ltuid"]
            return ltuid

        def get_user_uid(id, data):
            uid = data[id]["uid"]
            return uid

        async def get_user_stats(ltoken, ltuid, uid):
            gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
            genshin_stats = await gc.get_genshin_user(uid)
            anemoculus = genshin_stats.stats.anemoculi
            geoculus = genshin_stats.stats.geoculi
            electroculus = genshin_stats.stats.electroculi
            dendroculus = genshin_stats.stats.dendroculi
            return [anemoculus, geoculus, electroculus, dendroculus]

        for user in all_users: 
            try:
                ltoken = get_user_ltoken(id = user, data = all_users)
                ltuid = get_user_ltuid(id = user, data = all_users)
                uid = get_user_uid(id = user, data = all_users)
                user_stats = await get_user_stats(ltoken = ltoken, ltuid = ltuid, uid = uid)
                data = {"anemoculi": user_stats[0],
                        "geoculi": user_stats[1],
                        "electroculi": user_stats[2],
                        "dendroculi": user_stats[3],
                        "total": sum(user_stats)}
                # print(user, data)
                database.child("boon").child("notes").child("lb").child(user).update(data)
                time.sleep(0.5)
                print(f"{uid}")
            except:
                print("Invalid cookies")
        
        

    @oculi_update.before_loop
    async def before_printer(self):
        print('waiting for oculi index update...')
        await self.bot.wait_until_ready()
        
async def setup(bot):
    await bot.add_cog(pulladd(bot))