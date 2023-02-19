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
            data = {"time": added_time, "channel": interaction.channel.id, "specific": False}
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
                print("test")
                if database.child("boon").child("notes").child("users").child(ctx.author.id).get().val():
                    user = database.child("boon").child("notes").child("users").child(ctx.author.id).get().val()
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
                        print(e)
                        output = None
                        return

                    try:
                        signature = f"\"{output['playerInfo']['signature']}\""
                    except:
                        signature = "None"

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
                    embed.add_field(name="<:WL:1036184269950820422> **New!**", value="Set a reminder when your resin reaches a certain amount with `.rr <target amout>`")
                    
                    genshin_stats = await gc.get_genshin_user(uid)
                    embed.add_field(
                        name="Stats",
                        value=f"**Days Active:** {genshin_stats.stats.days_active}\n**Characters:**{genshin_stats.stats.characters}\n<:anemoculus:1037646266185818152> {genshin_stats.stats.anemoculi} <:geoculus:1037646330895552552> {genshin_stats.stats.geoculi} <:electroculus:1037646373618733138> {genshin_stats.stats.electroculi} <:dendroculus:1037646414689345537> {genshin_stats.stats.dendroculi}\n<:common_chest:1037649653145030697> {genshin_stats.stats.common_chests} <:exquisite_chest:1037649650645217341> {genshin_stats.stats.exquisite_chests} <:precious_chest:1037649648602591362>  {genshin_stats.stats.precious_chests}\n<:Luxurious_chest:1037649646677401660>  {genshin_stats.stats.luxurious_chests} <:remarkable_chest:1037649644748029994> {genshin_stats.stats.remarkable_chests} <:waypoint:1037650848349683782> {genshin_stats.stats.unlocked_waypoints} <:domain:1037650846277709854> {genshin_stats.stats.unlocked_domains}\n**Oculus Ranking:** #{oculi_rank} out of {oculi_lb_length}\n**Chest Ranking:** #{chest_rank} out of {oculi_lb_length}",
                        inline=True)
                    
                    if not database.child("boon").child("notes").child("users").child(ctx.author.id).child("settings").get().val():
                        if not database.child("boon").child("notes").child("reminders").child(ctx.author.id).get().val():
                            if notes.remaining_resin_recovery_time.seconds > 600:
                                await reply.edit(content="", embed=embed, view=buttonRemind(author=ctx.author.id, time=notes.remaining_resin_recovery_time.seconds))
                            elif notes.remaining_resin_recovery_time.seconds <= 600:
                                await reply.edit(content="", embed=embed)
                        else:
                            await reply.edit(content="", embed=embed, view=removeRemind(author=ctx.author.id))

                    elif database.child("boon").child("notes").child("users").child(ctx.author.id).child("settings").get().val():
                        user_settings = database.child("boon").child("notes").child("users").child(ctx.author.id).child("settings").get().val()
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

                elif not database.child("boon").child("notes").child("users").child(ctx.author.id).get().val():
                    await ctx.reply("Your Discord ID is not linked to a Boon notes account. Please register using </register:1056894402548736060>")
            except Exception as e:
                print(e)
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
                        print(e)
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
                print(e)
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
            await ctx.reply(f"An error occured. Please ping tofu.\n`{e}`")
        
async def setup(bot):
    await bot.add_cog(notesClass(bot))