import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
from urllib.request import Request, urlopen
import genshin
import asyncio
import time
from humanfriendly import format_timespan, parse_timespan
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


class ptlbClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ptlb cog is online.")


    @commands.command()
    async def ptlb(self,ctx, top=5):
        # users = database.child("boon").child("playtime").child("lb").shallow().get().val()

        # data = {'353228469154480129': {'username': '353228469154480129'}, '947526371041763389': {'username': '947526371041763389'}, '422339893138554882': {'username': '422339893138554882'}, '510999642687799297': {'username': '510999642687799297'}, '424726355977175040': {'username': '424726355977175040'}, '756683757821362247': {'username': '756683757821362247'}, '1048952675212996668': {'username': '1048952675212996668'}, '607824698130300943': {'username': '607824698130300943'}, '827050678689988649': {'username': '827050678689988649'}, '305711404747587585': {'username': '305711404747587585'}, '451894645304197121': {'username': '451894645304197121'}, '356869078578757646': {'username': '356869078578757646'}, '437745619684032512': {'username': '437745619684032512'}, '395888800888520705': {'username': '395888800888520705'}, '366434040292573184': {'username': '366434040292573184'}, '424751908658610179': {'username': '424751908658610179'}, '691804536133648475': {'username': '691804536133648475'}}

        # for user in users:
        #     username = await self.bot.fetch_user(user)
        #     username = str(username)[:-5]
        #     database.child('boon').child('playtime').child('lb').child(user).update({'username': username})

        # database.child('boon').child('playtime').child('lb').update(data)
        try:
            data = database.child('boon').child('playtime').child('lb').get().val()
            lb_data = {}

            for user in data:
                if int(user) == ctx.author.id:
                    username = f"{data[user]['username']} <:WL:1036184269950820422> (You)"
                else:
                    username = data[user]['username']
                lb_data.update({user:{
                                'username': username,
                                'duration': data[user]['total']
                }})
            
            sorted_data = sorted(lb_data.items(), key=lambda x: int(x[1]['duration']), reverse=True)
            message = ''
            index = 1
            found_me = False
            for _ in sorted_data:
                message += f"\n** #{index} {lb_data[_[0]]['username']}**\n{format_timespan(lb_data[_[0]]['duration'])}\n"
                index += 1
                if index == top + 1:
                    break
                if int(_[0]) == ctx.author.id:
                    found_me = True
                    
            if not found_me:
                for _ in sorted_data[index:]:
                    index += 1
                    if int(_[0]) == ctx.author.id:
                        message += f"\n** #{index} {lb_data[_[0]]['username']}**\n{format_timespan(lb_data[_[0]]['duration'])}\n"
                

            embed = discord.Embed(title='Who spent the most time on Genshin (2023)', description=f"{message}\n\n**NOTE:**\nYour playtime is only recorded if the following conditions are met:\n1. \"Genshin Impact\" is displayed on your Discord RPC\n2. You are not listening to Spotify before you close Genshin\nUse `.ptlb <number>` to see more members.\nUse `.ptindex` to retabulate data, do not use this command too fast.", color=3092790)
            await ctx.reply(embed=embed)
            


            embed = discord.Embed(title='Playtime Leaderboard')
        except Exception as e:
            print(f"ERROR: {e}")

    @commands.command()
    async def ptindex(self, ctx):
        await ctx.reply('Indexing...')
        try:
            pt_data = database.child("boon").child("playtime").get().val()
        
            lb = {}

            for user in pt_data:
                print(user)
                try:
                    username = await self.bot.fetch_user(user)
                    username = str(username)[:-5]
                except Exception as e:
                    print(f'ERROR: {e}')
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
            
                except Exception as e:
                    print(f"ERROR in tabulation: {e}")
            database.child('boon').child('playtime').child('lb').update(lb)
            await ctx.reply('Indexing Complete.')
        except Exception as e:
            await ctx.reply(f"ERROR: {e}")
        
async def setup(bot):
    await bot.add_cog(ptlbClass(bot))