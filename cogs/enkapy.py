import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
from humanfriendly import format_timespan
from enkanetwork import EnkaNetworkAPI
from enkanetwork.model.stats import Stats
import asyncio
from enkanetwork import Assets
import sys

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
enclnt = EnkaNetworkAPI()
assets = Assets()

class SelectCharacter(discord.ui.Select):
    def __init__(self, character_list, nickname):
        self.character_list = character_list
        self.nickname = nickname
        option_list = []
        for character in character_list:
            option_list.append(discord.SelectOption(label=f"{character['Index'] + 1} {character['Name']}"))

        super().__init__(placeholder="Select character", max_values=1, min_values=1, options=option_list)
    async def callback(self, interaction: discord.Interaction):
        selected = int(self.values[0][0]) - 1
        print(self.character_list)
        embed = discord.Embed(title=f"{self.nickname}'s Profile", description=f"**{self.character_list[selected]['Name']}**\n**Level:** {self.character_list[selected]['Level']}\n<:critrate:1076738384560660520> {self.character_list[selected]['Crit']}\n<:critdmg:1076738380206973020> {self.character_list[selected]['CritDMG']}")
        embed.set_thumbnail(url=self.character_list[selected]['Icon'])
        await interaction.response.edit_message(embed=embed)

class SelectCharacterView(discord.ui.View):
    def __init__(self, *, timeout=100, character_list, nickname):
        super().__init__(timeout=timeout)
        self.add_item(SelectCharacter(character_list=character_list, nickname=nickname))

class enkapy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("enkapy cog is online.")

    @commands.command()
    async def enkaIndex(self,ctx):
        async with enclnt:
            
            #### old_enkaIndex.py.old

            try:
                users = database.child('boon').child('notes').child('users').get().val()
                for user in users:
                    uid = users[user]['uid']
                    # print(uid)
                    data = await enclnt.fetch_user_by_uid(uid)
                    for character_raw in data.characters:
                        record = {character_raw.name:{'level': character_raw.level}}
                        database.child('boon').child('characters').child(user).update(record)
                        for stat in character_raw.stats:
                            if stat[0] == 'FIGHT_PROP_CRITICAL':
                                crit_data = {'Crit': stat[1].to_percentage_symbol()}
                                database.child('boon').child('characters').child(user).child(character_raw.name).update(crit_data)
                            elif stat[0] == 'FIGHT_PROP_CRITICAL_HURT':
                                critDMG_data = {'CritDMG': stat[1].to_percentage_symbol()}
                                database.child('boon').child('characters').child(user).child(character_raw.name).update(critDMG_data)
            
            except Exception as e:
                print(f"ERROR: {e}")

    @commands.command()
    async def enka(self,ctx):
        async with enclnt:
            try:
                users = database.child('boon').child('notes').child('users').get().val()
                for user in users:
                    username = await self.bot.fetch_user(user)
                    username = str(username)[:-5]
                    user_data = {'username': username}
                    uid = users[user]['uid']
                    data = await enclnt.fetch_user_by_uid(uid)
                    try:

                        for character_raw in data.characters:
                            for stat in character_raw.stats:
                                if stat[0] == 'FIGHT_PROP_CRITICAL':
                                    crit = stat[1].to_percentage_symbol()[:-1]
                                elif stat[0] == 'FIGHT_PROP_CRITICAL_HURT':
                                    critdmg = stat[1].to_percentage_symbol()[:-1]
                            cvr = round(float(crit))*2 + round(float(critdmg))
                            cv = float(crit)*2 + float(critdmg)
                            record = {cvr: {
                                'Name': character_raw.name,
                                'Level': character_raw.level,
                                'critdmg': critdmg,
                                'crit': crit,
                                'cv': round(cv, 2)
                            }}
                            user_data.update(record)
                        
                        database.child('boon').child('cvlb').child(user).update(user_data)
                        # print(user_data)
                    except Exception as e:
                        print(f'Error in 1 {e}')
                    
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)


    @commands.command()
    async def cvlb(self, ctx, top = 5):
        data = database.child('boon').child('cvlb').get().val()
        lb_data = {}
        for user in data:
            cvs = list(data[user])
            cvs.remove('username')
            highest = cvs.pop()
            # print(f"======={data[user]['username']}=======")
            character = data[user][highest]
            # print(character['Name'])
            # print(character['cv'])
            lb_data.update({user:{
                            'cv': character['cv'],
                            'character': character['Name'],
                            'username': data[user]['username']}})

        sorted_data = sorted(lb_data.items(), key=lambda x: int(x[1]['cv']), reverse=True)
        message = ''
        index = 1
        for _ in sorted_data:
            message += f"\n** #{index} {lb_data[_[0]]['username']}**\n({lb_data[_[0]]['cv']} - {lb_data[_[0]]['character']})\n"
            index += 1
            if index == top + 1:
                break
        embed = discord.Embed(title='Who has the highest CV?', description=f"{message}", color=3092790)
        embed2 = discord.Embed(title='Note', description="\n\n**NOTE:** This is just a proof of concept. CVs are skewed because characters have different ascension stats and weapons, and it's not always about CV ^^\n\nCVs are tabulated once a day.\nDo `.cvlb <number>` to get a longer leaderboard.", color=3092790)
        await ctx.reply(embed=embed)
        await ctx.send(embed=embed2)
        
async def setup(bot):
    await bot.add_cog(enkapy(bot))