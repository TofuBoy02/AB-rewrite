import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
import asyncio
import genshin
from humanfriendly import format_timespan, parse_timespan
import datetime
from urllib.request import Request, urlopen
import time
import json
from collections import OrderedDict
import sys
import requests
import ssl

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

element_emojis = {
    "Rock": "<:geo:1108681874647285781>",
    "Wind": "<:anemo:1108682012610531349>",
    "Electric": "<:electro:1108682279284387871>",
    "Grass": "<:dendro:1108682341695619154>",
    "Water": "<:hydro:1108682390768992327>",
    "Fire": "<:pyro:1108682468065824789>",
    "Ice": "<:cryo:1108682516564561981>"
}

firebase = pyrebase.initialize_app(config)
database = firebase.database()


class removeRemind(discord.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__(timeout=100)
    

    @discord.ui.button(label="Remove reminder", style=discord.ButtonStyle.red, emoji="<:cross:772100763659927632>")
    async def removeremindbutton(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id == self.author:
            button.disabled = True
            await interaction.message.edit(view=self)
            database.child("boon").child("notes").child("reminders").child(self.author).remove()
            await interaction.response.send_message(f"Reminder has been removed.")
            

class buttonRemind(discord.ui.View):
    def __init__(self, author, time):
        self.author = author
        self.time = time
        super().__init__(timeout=100)
    

    @discord.ui.button(label="Notify 10m before cap", style=discord.ButtonStyle.green, emoji="🔔")
    async def remindbutton(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id == self.author:
            button.disabled = True
            await interaction.message.edit(view=self)
            added_time = int(time.time()) + int(self.time) - 600
            human_time = format_timespan(num_seconds=self.time-600, max_units=2)
            data = {"time": added_time, "channel": str(interaction.channel.id), "specific": False}
            database.child("boon").child("notes").child("reminders").child(interaction.user.id).update(data)
            await interaction.response.send_message(f"Okay, I'll check your resin in {human_time} and tell you if it's almost capped! You can still use you resin, and I'll readjust my timer accordingly~")


class notesClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("notes cog is online.")

    async def on_error(self, error):
        print(error)

    def get_rank(sorted_data_oculi, sorted_data_chest, user):
        user_str = str(user)
        rank_oculi = 1
        rank_chest = 1
        for key in sorted_data_oculi.keys():
            if key == user_str:
                break
            rank_oculi += 1
        for key in sorted_data_chest.keys():
            if key == user_str:
                break
            rank_chest += 1
        return {"oculi_rank": rank_oculi,
                "chest_rank": rank_chest}
    
    def unix_to_years_months(unix_timestamp):
        now = datetime.datetime.now()
        timestamp = datetime.datetime.fromtimestamp(unix_timestamp)
        delta = now - timestamp

        years = delta.days // 365
        months = (delta.days % 365) // 30

        if years == 0:
            if months == 0:
                return 'less than a month ago'
            elif months == 1:
                return '1 month ago'
            else:
                return '{} months ago'.format(months)
        elif years == 1:
            if months == 0:
                return '1 year ago'
            elif months == 1:
                return '1 year and 1 month ago'
            else:
                return '1 year and {} months ago'.format(months)
        else:
            if months == 0:
                return '{} years ago'.format(years)
            elif months == 1:
                return '{} years and 1 month ago'.format(years)
            else:
                return '{} years and {} months ago'.format(years, months)
    
    def unix_days_ago(unix_timestamp):
        now = datetime.datetime.now()
        timestamp = datetime.datetime.fromtimestamp(unix_timestamp)
        delta = now - timestamp

        return delta.days
    
    def unix_to_date(unix_timestamp):
        timestamp = datetime.datetime.fromtimestamp(unix_timestamp)
        formatted_date = timestamp.strftime('%B %d, %Y')
        return formatted_date
    
    def get_start_date(uid):
        url = f'https://genshin.aza.gg/api/game/genshin/check-date-uid-static/u/{uid}'
        headers = {
            'authority': 'genshin.aza.gg',
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
            'content-type': 'application/json',
            'cookie': 'adfit_sdk_id=d56d62ae-d1f5-43e1-a1a4-d6eadff92de0; lang=en',
            'origin': 'https://genshin.aza.gg',
            'referer': f'https://genshin.aza.gg/uid/{uid}',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0'
        }
        data = {}

        response = requests.post(url, headers=headers, json=data)

        return response.json()
    
    def get_akasha(uid):
        url = f"https://akasha.cv/api/getCalculationsForUser/{uid}"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
            "Connection": "keep-alive",
            "Cookie": "connect.sid=s%3A7p_AT9cdA7-hBcREzKT9wZzpZMUhDmMM.TWKSIHvPK1Y2l1pnKT81KkhPmsmR%2BFMg3Y60u5s9HNc",
            "If-None-Match": 'W/"a5d8-6a0G7Cws5554RTURi1zZpOiPOns"',
            "Referer": "https://akasha.cv/profile/813180074",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }
        # ssl._create_default_https_context = ssl._create_unverified_context()

        response = requests.get(url, headers=headers, timeout=3, verify='./cacert.pem')
        # print(response.json())
        return response.json()
    
    def extract_calculations(data):
        calculations_list = []

        for character_data in data['data']:
            character_id = character_data['characterId']
            character_name = character_data['name']
            calculations = character_data['calculations']

            character_calculations = []
            for calculation_id, calculation in calculations.items():
                calculation_info = {
                    'calculationId': calculation_id,
                    'ranking': calculation['ranking'],
                    'outOf': calculation['outOf']
                }

                # Check if variant exists and use the display name instead of the short name
                variant = calculation.get('variant')
                if variant:
                    calculation_info['name'] = variant['displayName']
                else:
                    calculation_info['name'] = calculation['short']

                character_calculations.append(calculation_info)

            character_info = {
                'characterId': character_id,
                'characterName': character_name,
                'calculations': character_calculations
            }

            calculations_list.append(character_info)

        return calculations_list

    
    def get_lowest_ranking(data):
        result = []

        for character_data in data:
            character_name = character_data['characterName']
            character_id = character_data['characterId']
            calculations = character_data['calculations']

            lowest_ranking_percentage = float('inf')
            lowest_ranking_calculation = None

            for calculation in calculations:
                calculation_name = calculation['name']
                ranking = calculation['ranking']
                out_of = calculation['outOf']

                ranking_percentage = ranking / out_of

                if ranking_percentage < lowest_ranking_percentage:
                    lowest_ranking_percentage = ranking_percentage
                    lowest_ranking_calculation = {
                        'calculationName': calculation_name,
                        'ranking': ranking,
                        'outOf': out_of,
                        'rankingPercentage': ranking_percentage
                    }

            character_info = {
                'characterName': character_name,
                'calculation': lowest_ranking_calculation,
                'characterId': character_id
            }

            result.append(character_info)

        return result
    
    def sort_akasha_ranking(data):
        sorted_data = sorted(data, key=lambda x: x['calculation']['rankingPercentage'])
        return sorted_data
    
    def format_percentage(value):
        percentage = round(value * 100)
        return "{}%".format(percentage)

    def get_lb(user):
        data = database.child("boon").child("notes").child("lb").get().val()
        sorted_data_oculi = OrderedDict(sorted(data.items(), key=lambda x: x[1]['total'], reverse=True))
        sorted_data_chest = OrderedDict(sorted(data.items(), key=lambda x: x[1]['total_chest'], reverse=True))
        rank = notesClass.get_rank(sorted_data_oculi = sorted_data_oculi, sorted_data_chest = sorted_data_chest, user = user)
        number_of_users = len(data)
        return {"oculi_rank": rank["oculi_rank"],
                "chest_rank": rank["chest_rank"],
                "users": number_of_users}

    @commands.command()
    async def n(self,ctx, alt=None):
        if alt is None:
            try:
                if user := database.child("boon").child("notes").child("users").child(ctx.author.id).get().val():
                    # user = database.child("boon").child("notes").child("users").child(ctx.author.id).get().val()
                    ltuid = user["ltuid"]
                    ltoken = user["ltoken"]
                    gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
                    uid = user["uid"]
                    name = ctx.author.name
                    ranking_data = notesClass.get_lb(user = ctx.author.id)
                    oculi_rank = ranking_data["oculi_rank"]
                    chest_rank = ranking_data["chest_rank"]
                    oculi_lb_length = ranking_data["users"]
                    
                    reply = await ctx.reply("Fetching data...")
                    notes = await gc.get_genshin_notes(uid)

                    resin_remaining_time = format_timespan(notes.remaining_resin_recovery_time, max_units=2)
                    
                    if resin_remaining_time == "0 seconds":
                        resin_remaining_time = "rip lol"

                    try:
                        transformer_recovery_time = int(notes.transformer_recovery_time.timestamp())
                    except:
                        transformer_recovery_time = False

                    try:
                        current_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                    except:
                        await ctx.reply("Something went wrong with calculating `current_time`. Please try again later.")
                        return

                    if transformer_recovery_time == current_time:
                        transformer = "**Off-Cooldown** :warning:"
                    elif transformer_recovery_time == False:
                        transformer = "Couldn't fetch"
                    else:
                        current_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                        transformer = f"{format_timespan(transformer_recovery_time - current_time, max_units=2)}"

                    try:
                        start_date = notesClass.get_start_date(uid)
                        start_date_version = start_date['data']['version'].replace(';', '.')
                        start_date_day = start_date['data']['version_date']
                        start_date_unix = start_date['data']['unix_time']
                        start_date_humanfriendly = notesClass.unix_to_years_months(start_date_unix)
                        start_date_date = notesClass.unix_to_date(start_date_unix)
                    except Exception as e:
                        print(e)
                        start_date = 0


                    try:
                        
                        url = f"https://enka.network/api/uid/{uid}"
                        print(url)
                        request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                        webpage = urlopen(request_site).read()
                        output = json.loads(webpage.decode('utf-8'))
                        f = open('./characters.json')
                        characters_output = json.load(f)
                        profile_character_id = f"{output['playerInfo']['profilePicture']['avatarId']}"
                        character_id_ui = f"{characters_output[profile_character_id]['SideIconName']}"
                        character_id_ui_front = character_id_ui.replace('Side_', '')
                        character_id_ui_url = f"https://enka.network/ui/{character_id_ui_front}.png"
                    except Exception as e:
                        print(f'001 {e}')
                        output = None
                        

                    try:
                        signature = f"\"{output['playerInfo']['signature']}\""
                    except Exception as e:
                        print(f'0002 {e}')
                        signature = None
                    if output != None:
                        player_name = output['playerInfo']['nickname']
                    else:
                        player_name = ctx.author.name
                    embed = discord.Embed(
                        title=f"{player_name}'s Live Notes",
                        color=ctx.author.color,
                        description=f"<:resin:950411358569136178> {notes.current_resin}/{notes.max_resin} \n **Time until capped:** {resin_remaining_time} \n<:transformer:967334141681090582> {transformer}\n<:Item_Realm_Currency:950601442740301894> {notes.current_realm_currency}/{notes.max_realm_currency} \n **Expeditions:** {len(notes.expeditions)}/{notes.max_expeditions} \n <:Icon_Commission:950603084701253642> {notes.completed_commissions}/4 \n **Claimed Guild Rewards:** {notes.claimed_commission_reward} \n **Remaining weekly boss discounts:** {notes.remaining_resin_discounts}\n<:blank:1036569081345757224>"
                    )
                    if output != None:
                        embed.add_field(
                            name="<:paimon:1036568819646341180> Genshin Profile",
                            value= f"**Username:** {output['playerInfo']['nickname']}\n<:signature:1036183906950590515> {signature}\n<:AR:1036183121760104448> **AR:** {output['playerInfo']['level']}\n<:WL:1036184269950820422> **World Level: ** {output['playerInfo']['worldLevel']}\n**Achievements:** {output['playerInfo']['finishAchievementNum']}\n<:abyss:1036184565422772305> {output['playerInfo']['towerFloorIndex']}-{output['playerInfo']['towerLevelIndex']}\n**Started:** Version {start_date_version}, Day {start_date_day}\n{start_date_date}\n({start_date_humanfriendly})\n<:blank:1036569081345757224>",
                            inline=True)
                        embed.set_thumbnail(url=character_id_ui_url)

                    

                    else:
                        pass

                   
                    
                    
                    genshin_stats = await gc.get_genshin_user(uid)
                    embed.add_field(
                        name="Stats",
                        value=f"**Days Active:** {genshin_stats.stats.days_active}\n**Days Missed:** {notesClass.unix_days_ago(start_date_unix) - int(genshin_stats.stats.days_active)}\n**Characters:** {genshin_stats.stats.characters}\n<:anemoculus:1037646266185818152> {genshin_stats.stats.anemoculi} <:geoculus:1037646330895552552> {genshin_stats.stats.geoculi} <:electroculus:1037646373618733138> {genshin_stats.stats.electroculi} <:dendroculus:1037646414689345537> {genshin_stats.stats.dendroculi}\n<:common_chest:1037649653145030697> {genshin_stats.stats.common_chests} <:exquisite_chest:1037649650645217341> {genshin_stats.stats.exquisite_chests} <:precious_chest:1037649648602591362>  {genshin_stats.stats.precious_chests}\n<:Luxurious_chest:1037649646677401660>  {genshin_stats.stats.luxurious_chests} <:remarkable_chest:1037649644748029994> {genshin_stats.stats.remarkable_chests} <:waypoint:1037650848349683782> {genshin_stats.stats.unlocked_waypoints} <:domain:1037650846277709854> {genshin_stats.stats.unlocked_domains}\n**Oculus Ranking:** #{oculi_rank} out of {oculi_lb_length}\n**Chest Ranking:** #{chest_rank} out of {oculi_lb_length}",
                        inline=True)
                    
                    try:
                        akasha_stats = notesClass.get_akasha(uid)
                        extracted_akasha = notesClass.extract_calculations(akasha_stats)
                        pretty_akasha = notesClass.get_lowest_ranking(extracted_akasha)
                        sorted_pretty_akasha = notesClass.sort_akasha_ranking(pretty_akasha)
                        f = open('./characters.json')
                        characters_output = json.load(f)
                        # print(pretty_akasha)
                        akasha_description = ""
                        if not akasha_stats['data']:
                            embed.add_field(
                            name="<:akasha:1108685838646263888> Akasha Ranking",
                            value= f"Can't fetch data, please try to initiate your account on the website first",
                            inline=False)
                        else:
                            for data in sorted_pretty_akasha:
                                character_element_name = characters_output[str(data['characterId'])]['Element']
                                character_element = element_emojis.get(character_element_name, "")
                                character_name = data['characterName']
                                calculation = data['calculation']
                                calculation_name = calculation['calculationName']
                                ranking_percentage = calculation['rankingPercentage']
                                formatted_percentage =notesClass.format_percentage(ranking_percentage)
                                akasha_description += f"\n{character_element}**{character_name} ({calculation_name})**: Top {formatted_percentage}"
                            embed.add_field(
                                name="<:akasha:1108685838646263888> Akasha Ranking",
                                value= f"{akasha_description}",
                                inline=False)
                    except requests.Timeout:
                        embed.add_field(
                            name="<:akasha:1108685838646263888> Akasha Ranking",
                            value= f"Akasha took too long to respond.",
                            inline=False)

                    except Exception as e:
                        print(f"akasha error: {e}")
                        embed.add_field(
                            name="<:akasha:1108685838646263888> Akasha Ranking",
                            value= f"Can't fetch data, please try to initiate your account on the website first.",
                            inline=False)
                    
                    if not database.child("boon").child("notes").child("users").child(ctx.author.id).child("settings").get().val():
                        if not database.child("boon").child("notes").child("reminders").child(ctx.author.id).get().val():
                            if notes.remaining_resin_recovery_time.seconds > 600:
                                await reply.edit(content="", embed=embed, view=buttonRemind(author=ctx.author.id, time=notes.remaining_resin_recovery_time.seconds))
                            elif notes.remaining_resin_recovery_time.seconds <= 600:
                                await reply.edit(content="", embed=embed)
                        else:
                            await reply.edit(content="", embed=embed, view=removeRemind(author=ctx.author.id))

                    elif user_settings := database.child("boon").child("notes").child("users").child(ctx.author.id).child("settings").get().val():
                        # user_settings = database.child("boon").child("notes").child("users").child(ctx.author.id).child("settings").get().val()
                        if user_settings["show_note_buttons"] == True:
                            if not database.child("boon").child("notes").child("reminders").child(ctx.author.id).get().val():
                                if notes.remaining_resin_recovery_time.seconds > 600:
                                    await reply.edit(content="", embed=embed, view=buttonRemind(author=ctx.author.id, time=notes.remaining_resin_recovery_time.seconds))
                                elif notes.remaining_resin_recovery_time.seconds <= 600:
                                    await reply.edit(content="", embed=embed)
                            else:
                                await reply.edit(content="", embed=embed, view=removeRemind(author=ctx.author.id))
                        elif user_settings["show_note_buttons"] == False:
                            await reply.edit(content="", embed=embed)

                # elif not database.child("boon").child("notes").child("users").child(ctx.author.id).get().val():
                else:
                    await ctx.reply("Your Discord ID is not linked to a Boon notes account. Please register using </register:1056894402548736060>")
            except Exception as e:
                print(f'003 {e}')
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                await ctx.reply(f"An error occured. Please ping tofu.\n`{e}`")

            ##### Update oculi index #####
            try:
                data = {"anemoculi": genshin_stats.stats.anemoculi,
                        "geoculi": genshin_stats.stats.geoculi,
                        "electroculi": genshin_stats.stats.electroculi,
                        "dendroculi": genshin_stats.stats.dendroculi,
                        "total": genshin_stats.stats.anemoculi + genshin_stats.stats.geoculi + genshin_stats.stats.electroculi + genshin_stats.stats.dendroculi,
                        "common_chest": genshin_stats.stats.common_chests,
                        "exquisite_chest": genshin_stats.stats.exquisite_chests,
                        "precious_chest": genshin_stats.stats.precious_chests,
                        "luxurious_chest": genshin_stats.stats.luxurious_chests,
                        "remarkable_chest": genshin_stats.stats.remarkable_chests,
                        "total_chest": genshin_stats.stats.common_chests + genshin_stats.stats.exquisite_chests + genshin_stats.stats.precious_chests + genshin_stats.stats.luxurious_chests + genshin_stats.stats.remarkable_chests}
                database.child("boon").child("notes").child("lb").child(ctx.author.id).update(data)
            except:
                print("Could not update oculi data")
        
        elif alt is not None:
            try:
                if database.child("boon").child("notes").child("users").child(ctx.author.id).child("alts").child(alt).get().val():
                    user = database.child("boon").child("notes").child("users").child(ctx.author.id).child("alts").child(alt).get().val()
                    ltuid = user["ltuid"]
                    ltoken = user["ltoken"]
                    gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
                    uid = user["uid"]
                    name = ctx.author.name
                    
                    reply = await ctx.reply("Fetching data...")
                    notes = await gc.get_genshin_notes(uid)

                    resin_remaining_time = format_timespan(notes.remaining_resin_recovery_time, max_units=2)
                    
                    if resin_remaining_time == "0 seconds":
                        resin_remaining_time = "rip lol"

                    try:
                        transformer_recovery_time = int(notes.transformer_recovery_time.timestamp())
                    except:
                        transformer_recovery_time = False

                    try:
                        current_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                    except:
                        await ctx.reply("Something went wrong with calculating `current_time`. Please try again later.")
                        return

                    if transformer_recovery_time == current_time:
                        transformer = "**Off-Cooldown** :warning:"
                    elif transformer_recovery_time == False:
                        transformer = "Couldn't fetch"
                    else:
                        current_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                        transformer = f"{format_timespan(transformer_recovery_time - current_time, max_units=2)}"

                    try:
                        
                        url = f"https://enka.network/api/uid/{uid}"
                        request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                        webpage = urlopen(request_site).read()
                        output = json.loads(webpage.decode('utf-8'))
                        f = open('./characters.json')
                        characters_output = json.load(f)
                        profile_character_id = f"{output['playerInfo']['profilePicture']['avatarId']}"
                        character_id_ui = f"{characters_output[profile_character_id]['SideIconName']}"
                        character_id_ui_front = character_id_ui.replace('Side_', '')
                        character_id_ui_url = f"https://enka.network/ui/{character_id_ui_front}.png"
                    except Exception as e:
                        print(f'004 {e}')
                        output = None

                    try:
                        signature = f"\"{output['playerInfo']['signature']}\""
                    except:
                        signature = "None"

                    ####### OCULUS RANKING #######
                    

                    embed = discord.Embed(
                        title=f"{output['playerInfo']['nickname']}'s Live Notes",
                        color=ctx.author.color,
                        description=f"<:resin:950411358569136178> {notes.current_resin}/{notes.max_resin} \n **Time until capped:** {resin_remaining_time} \n<:transformer:967334141681090582> {transformer}\n<:Item_Realm_Currency:950601442740301894> {notes.current_realm_currency}/{notes.max_realm_currency} \n **Expeditions:** {len(notes.expeditions)}/{notes.max_expeditions} \n <:Icon_Commission:950603084701253642> {notes.completed_commissions}/4 \n **Claimed Guild Rewards:** {notes.claimed_commission_reward} \n **Remaining weekly boss discounts:** {notes.remaining_resin_discounts}\n<:blank:1036569081345757224>"
                    )
                    if output != None:
                        embed.add_field(
                            name="<:paimon:1036568819646341180> Genshin Profile",
                            value= f"**Username:** {output['playerInfo']['nickname']}\n<:signature:1036183906950590515> {signature}\n<:AR:1036183121760104448> **AR:** {output['playerInfo']['level']}\n<:WL:1036184269950820422> **World Level: ** {output['playerInfo']['worldLevel']}\n**Achievements:** {output['playerInfo']['finishAchievementNum']}\n<:abyss:1036184565422772305> {output['playerInfo']['towerFloorIndex']}-{output['playerInfo']['towerLevelIndex']}\n<:blank:1036569081345757224>",
                            inline=True)
                        embed.set_thumbnail(url=character_id_ui_url)
                    else:
                        pass
                    genshin_stats = await gc.get_genshin_user(uid)
                    embed.add_field(
                        name="Stats",
                        value=f"**Days Active:** {genshin_stats.stats.days_active}\n**Characters:**{genshin_stats.stats.characters}\n<:anemoculus:1037646266185818152> {genshin_stats.stats.anemoculi} <:geoculus:1037646330895552552> {genshin_stats.stats.geoculi} <:electroculus:1037646373618733138> {genshin_stats.stats.electroculi} <:dendroculus:1037646414689345537> {genshin_stats.stats.dendroculi}\n<:common_chest:1037649653145030697> {genshin_stats.stats.common_chests} <:exquisite_chest:1037649650645217341> {genshin_stats.stats.exquisite_chests} <:precious_chest:1037649648602591362>  {genshin_stats.stats.precious_chests}\n<:Luxurious_chest:1037649646677401660>  {genshin_stats.stats.luxurious_chests} <:remarkable_chest:1037649644748029994> {genshin_stats.stats.remarkable_chests} <:waypoint:1037650848349683782> {genshin_stats.stats.unlocked_waypoints} <:domain:1037650846277709854> {genshin_stats.stats.unlocked_domains}",
                        inline=True)
                    
        
                    await reply.edit(content="", embed=embed)

                elif database.child("boon").child("notes").child("users").child(ctx.author.id).child("alts").get().val():
                    alt_names = ""

                    data = database.child("boon").child("notes").child("users").child(ctx.author.id).get().val()
                    # print(data)
                    alts = data["alts"]
                    for i, j in alts.items():
                        alt_names += f"\n• {i}"
                    embed = discord.Embed(title="Alt account not found.", description=f"Please choose one of these:{alt_names}", color=3092790)
                    await ctx.reply(embed=embed)
                else:
                    embed = discord.Embed()
                    await ctx.reply("This alt account is not found. You have no alt accounts registered.")
            except Exception as e:
                print(f'005 {e}')
                await ctx.reply(f"An error occured. Please ping tofu.\n`{e}`")


    @commands.command()
    async def acc(self, ctx):
        try:
            if database.child("boon").child("notes").child("users").child(ctx.author.id).get().val():
                user = database.child("boon").child("notes").child("users").child(ctx.author.id).get().val()
                ltuid = user["ltuid"]
                ltoken = user["ltoken"]
                gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
                uid = user["uid"]
                name = ctx.author.name

                reply = await ctx.reply(f"Digging HoyoVerse's database <a:Loading:1035066128080318494>")
                gameAccounts = await gc.get_game_accounts()
                
                embed = discord.Embed(title=f"{name}'s Game Accounts",
                                        color=ctx.author.color,
                                        description="")
                for accounts in gameAccounts:
                    if str(accounts.game_biz) == "bh3_global":
                        game = "Honkai Impact 3"
                    elif str(accounts.game_biz) == "nxx_global":
                        game = "Tears of Themis"
                    elif str(accounts.game_biz) == "hk4e_global":
                        game = "Genshin Impact"
                    else:
                        pass
                    embed.add_field(name=f"{game}",value=f"Name: {accounts.nickname}\nUID: {accounts.uid}\n Level: {accounts.level}\nServer: {accounts.server_name}")

                try:
                    await ctx.author.send(embed=embed)
                except:
                    await reply.edit(
                        content="I can't send you a DM! Please open your DMs."
                        )
                    return
                await reply.edit(content="Check your DMs!")



            elif not database.child("boon").child("notes").child("users").child(ctx.author.id).get().val():
                await ctx.reply("Your Discord ID is not linked to a Boon notes account. Please register using </register:1056894402548736060>")

        except Exception as e:
            print(f'006 {e}')
            await ctx.reply(f"An error occured. Please ping tofu.\n`{e}`")
        
async def setup(bot):
    await bot.add_cog(notesClass(bot))