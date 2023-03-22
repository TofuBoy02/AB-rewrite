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


class oculiUpdate(commands.Cog):
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
            common_chest = genshin_stats.stats.common_chests
            exquisite_chest = genshin_stats.stats.exquisite_chests
            precious_chest = genshin_stats.stats.precious_chests
            luxurious_chest = genshin_stats.stats.luxurious_chests
            remarkable_chest = genshin_stats.stats.remarkable_chests
            achievements = genshin_stats.stats.achievements
            # return [anemoculus, geoculus, electroculus, dendroculus]
            return {"anemoculus": anemoculus,
                    "geoculus": geoculus,
                    "electroculus": electroculus,
                    "dendroculus": dendroculus,
                    "total_oculus": anemoculus + geoculus + electroculus + dendroculus,
                    "common_chest": common_chest,
                    "exquisite_chest": exquisite_chest,
                    "precious_chest": precious_chest,
                    "luxurious_chest": luxurious_chest,
                    "remarkable_chest": remarkable_chest,
                    "total_chest": common_chest + exquisite_chest + precious_chest + luxurious_chest + remarkable_chest,
                    "achievements": achievements}

        for user in all_users: 
            try:
                ltoken = get_user_ltoken(id = user, data = all_users)
                ltuid = get_user_ltuid(id = user, data = all_users)
                uid = get_user_uid(id = user, data = all_users)
                user_stats = await get_user_stats(ltoken = ltoken, ltuid = ltuid, uid = uid)
                data = {"anemoculi": user_stats["anemoculus"],
                        "geoculi": user_stats['geoculus'],
                        "electroculi": user_stats['electroculus'],
                        "dendroculi": user_stats["dendroculus"],
                        "total": user_stats["total_oculus"],
                        "common_chest": user_stats["common_chest"],
                        "exquisite_chest": user_stats["exquisite_chest"],
                        "precious_chest": user_stats["precious_chest"],
                        "luxurious_chest": user_stats["luxurious_chest"],
                        "remarkable_chest": user_stats["remarkable_chest"],
                        "total_chest": user_stats["total_chest"],
                        "achievements": user_stats["achievements"]}
                # print(user, data)
                database.child("boon").child("notes").child("lb").child(user).update(data)
                time.sleep(0.5)
                # print(f"{uid}")
            except Exception as e:
                print(e)
        
            try:
                pt_data = database.child("boon").child("playtime").get().val()
            
                lb = {}

                for user in pt_data:
                    # print(user)
                    try:
                        username = await self.bot.fetch_user(user)
                        username = str(username)[:-5]
                    except:
                        pass
                    try:
                        user_total = 0
                        for year in pt_data[user]:
                            if year == 'settings':
                                pass
                            else:
                                for month in pt_data[user][year]:
                                    for session in pt_data[user][year][month]:
                                        user_total += int(pt_data[user][year][month][session]['Duration'])
                        # print(f"{user}, {user_total}")
                        if user_total != 0:
                            lb.update({user: {'total':user_total, 'username': username}})
                
                    except:
                        pass
                database.child('boon').child('playtime').child('lb').update(lb)
            except:
                pass
        

    @oculi_update.before_loop
    async def before_printer(self):
        print('waiting for oculi index update...')
        await self.bot.wait_until_ready()
        
async def setup(bot):
    await bot.add_cog(oculiUpdate(bot))