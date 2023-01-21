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
from discord import app_commands

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



class notesContext(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notes_ctx_menu = app_commands.ContextMenu(
            name='Live Notes',
            callback=self.notes_context, # set the callback of the context menu to "my_cool_context_menu"
        )
        self.bot.tree.add_command(self.notes_ctx_menu)
        

    async def notes_context(self, interaction: discord.Interaction, message: discord.Message):
        user_id = message.author.id
        try:
            await interaction.response.defer()
            user_data = database.child("boon").child("notes").child("users").child(user_id).get().val()
            ltuid = user_data["ltuid"]
            ltoken = user_data["ltoken"]
            uid = user_data["uid"]
            name = message.author.name
            gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
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
                await interaction.followup.send("Something wen't wrong with calculating time. Please try again.")
                return

            if transformer_recovery_time == current_time:
                transformer = "**Off-Cooldown** :warning:"
            elif transformer_recovery_time == False:
                transformer = "Couldn't fetch"
            else:
                current_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                transformer = f"{format_timespan(transformer_recovery_time - current_time, max_units=2)}"

            try:
                url = f"https://enka.shinshin.moe/u/{uid}/__data.json"
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
                print(f"enka error: {e}")
                output = None
            
            try:
                signature = f"\"{output['playerInfo']['signature']}\""
            except:
                signature = "None"

            embed = discord.Embed(
                    title=f"{name}'s Live Notes",
                    color=3092790,
                    description=f"<:resin:950411358569136178> {notes.current_resin}/{notes.max_resin} \n **Time until capped:** {resin_remaining_time} \n<:transformer:967334141681090582> {transformer}\n<:Item_Realm_Currency:950601442740301894> {notes.current_realm_currency}/{notes.max_realm_currency} \n **Expeditions:** {len(notes.expeditions)}/{notes.max_expeditions} \n <:Icon_Commission:950603084701253642> {notes.completed_commissions}/4 \n **Claimed Guild Rewards:** {notes.claimed_commission_reward} \n **Remaining weekly boss discounts:** {notes.remaining_resin_discounts}\n<:blank:1036569081345757224>"
                )
            if output != None:
                embed.add_field(
                    name="<:paimon:1036568819646341180> Genshin Profile",
                    value= f"**Username:** {output['playerInfo']['nickname']}\n<:signature:1036183906950590515> {signature}\n<:AR:1036183121760104448> **AR:** {output['playerInfo']['level']}\n<:WL:1036184269950820422> **World Level: ** {output['playerInfo']['worldLevel']}\n**Achievements:** {output['playerInfo']['finishAchievementNum']}\n<:abyss:1036184565422772305> {output['playerInfo']['towerFloorIndex']}-{output['playerInfo']['towerLevelIndex']}\n<:blank:1036569081345757224>",
                    inline=True)
                embed.set_thumbnail(url=character_id_ui_url)

            genshin_stats = await gc.get_genshin_user(uid)
            embed.add_field(
                name="Stats",
                value=f"**Days Active:** {genshin_stats.stats.days_active}\n**Characters:**{genshin_stats.stats.characters}\n<:anemoculus:1037646266185818152> {genshin_stats.stats.anemoculi} <:geoculus:1037646330895552552> {genshin_stats.stats.geoculi} <:electroculus:1037646373618733138> {genshin_stats.stats.electroculi} <:dendroculus:1037646414689345537> {genshin_stats.stats.dendroculi}\n<:common_chest:1037649653145030697> {genshin_stats.stats.common_chests} <:exquisite_chest:1037649650645217341> {genshin_stats.stats.exquisite_chests} <:precious_chest:1037649648602591362>  {genshin_stats.stats.precious_chests}\n<:Luxurious_chest:1037649646677401660>  {genshin_stats.stats.luxurious_chests} <:remarkable_chest:1037649644748029994> {genshin_stats.stats.remarkable_chests} <:waypoint:1037650848349683782> {genshin_stats.stats.unlocked_waypoints} <:domain:1037650846277709854> {genshin_stats.stats.unlocked_domains}",
                inline=True)

            await interaction.followup.send(embed=embed, ephemeral=True)


        except Exception as e:
            await interaction.followup.send("This user is not registered.", ephemeral=True)
            print(e)
        
            

async def setup(bot):
    await bot.add_cog(notesContext(bot))

# async def setup(bot):
#     await bot.add_cog(notesContext(bot), guilds=[discord.Object(id=980092176488886383)])