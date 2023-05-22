import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
import asyncio
import genshin
import requests
from collections import OrderedDict

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

class hsrclaim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("hsrclaim cog is online.")

    @commands.command()
    async def hsrclaim(self,ctx):
        try:
            users = database.child("boon").child("notes").child("users").get().val()
            shallow = dict(users)
            for user in shallow:
                username = await self.bot.fetch_user(user)
                user_data = shallow[user]
                ltoken = user_data["ltoken"]
                ltuid = user_data["ltuid"]
                uid = user_data["uid"]
                try:

                    url = "https://sg-public-api.hoyolab.com/event/luna/os/sign"
                    headers = {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Content-Type": "application/json;charset=UTF-8",
                        "Cookie": f"ltoken={ltoken}; ltuid={ltuid};",
                        "Origin": "https://act.hoyolab.com",
                        "Pragma": "no-cache",
                        "Referer": "https://act.hoyolab.com/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                        "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"'
                    }
                    data = {"act_id": "e202303301540311", "lang": "en-us"}

                    response = requests.post(url, headers=headers, json=data)
                    json_data = response.json()
                    retcode = json_data['retcode']
                    if retcode == 0:
                        success = True
                    elif retcode == -5003:
                        already_checked = True
                        # call function for already checked in here
                    else:
                        if json_data['message'] == 'Not logged in':
                            await ctx.send(f"<:cross:772100763659927632> {username}: Error: {json_data['message']} Please update your cookies, contact TofuBoy for assistance.")
                        else:
                            await ctx.send(f"<:cross:772100763659927632> {username}: Error: {json_data['message']}")



                except Exception as e:
                    await ctx.send(f"Error: {e}")

                if success or already_checked:
                    try:
                        url = "https://sg-public-api.hoyolab.com/event/luna/os/info?lang=en-us&act_id=e202303301540311"
                        headers = {
                            "Accept": "application/json, text/plain, */*",
                            "Accept-Language": "en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7",
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "Cookie": f"mi18nLang=en-us; ltoken={ltoken}; ltuid={ltuid}",
                            "Origin": "https://act.hoyolab.com",
                            "Pragma": "no-cache",
                            "Referer": "https://act.hoyolab.com/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                            "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
                            "sec-ch-ua-mobile": "?0",
                            "sec-ch-ua-platform": "\"Windows\""
                        }

                        response = requests.get(url, headers=headers)
                        response_data_days = response.json()
                        if response_data_days['data']['total_sign_day'] != 0:
                            if success:
                                await ctx.send(f"<:tick:772044532845772810> {username}: Successfully claimed Day {response_data_days['data']['total_sign_day']}. {response_data_days['data']['sign_cnt_missed']} days missed.")
                            elif already_checked:
                                await ctx.send(f"<:tick:772044532845772810> {username}: Already claimed Day {response_data_days['data']['total_sign_day']}. {response_data_days['data']['sign_cnt_missed']} days missed.")
                        if response_data_days['data']['total_sign_day'] == 0:
                            await ctx.send(f"<:cross:772100763659927632> {username}: Account error. 0 days claimed. Maybe user needs to log in on the check-in page first.")
                    except Exception as e:
                        print(f"Daily number error: {e}")

                        await asyncio.sleep(1)
        except Exception as e:
            print(f"Database error: {e}")

        

        
                
            
async def setup(bot):
    await bot.add_cog(hsrclaim(bot))
