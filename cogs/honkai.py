import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
from discord import app_commands
from discord.ext import commands
import genshin

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

honkaiUIDs = []

class SelectAcc(discord.ui.Select):
    def __init__(self):
        option_list = []
        if honkaiUIDs:
            for uid in honkaiUIDs:
                option_list.append(discord.SelectOption(label=f"{uid}"))
        elif not honkaiUIDs:
            discord.SelectOption(label=f"You do not have a Honkai account.")
        options = option_list
        super().__init__(placeholder="Select a UID", max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "You do not have a Honkai account.":
            await interaction.response.send_message("<@{interaction.user.id}> I already told you that you don't have a Honkai account, get help.")
            return
        await interaction.response.send_message(f"Successfully set your Honkai UID to {self.values[0]}. You can now use </honkai:1059362301360230400>.")
        data = {"huid": int(self.values[0])}
        database.child("boon").child("notes").child("users").child(interaction.user.id).update(data)

class SelectAccView(discord.ui.View):
    def __init__(self, *, timeout=100):
        super().__init__(timeout=timeout)
        self.add_item(SelectAcc())


class honkaiChronicle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print ('Register cog is online.')


    @app_commands.command(name="honkai", description="Register for autoclaim and live notes")
    async def honkai(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()

            if database.child("boon").child("notes").child("users").child(interaction.user.id).get().val() and database.child("boon").child("notes").child("users").child(interaction.user.id).child("huid").get().val():
                print("test")
                user = database.child("boon").child("notes").child("users").child(interaction.user.id).get().val()
                ltuid = user["ltuid"]
                ltoken = user["ltoken"]
                huid = user["huid"]
                gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
                notes = await gc.get_honkai_user(huid)
                embed = discord.Embed(title=f"{interaction.user.name}'s Honkai Battle Chronicles", color=interaction.user.color)
                try:
                    embed.add_field(name="Account", value=f"**Nickname:** {notes.info.nickname}\n**Server:** {notes.info.server}\n**Level:** {notes.info.level}\n**Days Active:** {notes.stats.active_days}\n**Achievements:** {notes.stats.achievements}\n<:blank:1036569081345757224>")
                except Exception as e:
                    print(e)
                try:
                    embed.add_field(name="Stats", value=f"**Battlesuts:** {notes.stats.battlesuits}\n**SSS Battlesuits:** {notes.stats.battlesuits_SSS}\n**Stigmata:** {notes.stats.stigmata}\n**5 Star Stigmatas:** {notes.stats.stigmata_5star}\n**Weapons:** {notes.stats.weapons}\n**5 Star Weapons:** {notes.stats.weapons_5star}\n**Outfits:** {notes.stats.outfits}\n<:blank:1036569081345757224>")
                except Exception as e:
                    print(e)
                try:
                    embed.add_field(name="Memorial Arena", value=f"**Ranking:** {notes.stats.memorial_arena.ranking}%\n**Rank:** {notes.stats.memorial_arena.raw_rank}\n**Score:** {notes.stats.memorial_arena.score}\n**Tier:** {notes.stats.memorial_arena.raw_tier}\n<:blank:1036569081345757224>")
                except Exception as e:
                    print(e)
                try:
                    embed.add_field(name="Abyss", value=f"**Q Singularis Rank:** {notes.stats.abyss.raw_q_singularis_rank}\n**Dirac Sea Rank:** {notes.stats.abyss.raw_dirac_sea_rank}\n**Score:** {notes.stats.abyss.score}\n**Tier:** {notes.stats.abyss.raw_tier}\n**Type:** {notes.stats.abyss.latest_type}\n<:blank:1036569081345757224>")
                except Exception as e:
                    print(e)
                try:
                    embed.add_field(name="Elysian Realm", value=f"**Highest Difficulty:** {notes.stats.elysian_realm.highest_difficulty}\n**Remembrance Sigils:** {notes.stats.elysian_realm.remembrance_sigils}\n**Highest Score:** {notes.stats.elysian_realm.highest_score}\n**Highest Floor:** {notes.stats.elysian_realm.highest_floor}\n<:blank:1036569081345757224>")
                except Exception as e:
                    print(e)

                embed.set_thumbnail(url=notes.info.icon)
                await interaction.followup.send(embed=embed)

            elif database.child("boon").child("notes").child("users").child(interaction.user.id).get().val() and not database.child("boon").child("notes").child("users").child(interaction.user.id).child("huid").get().val():
                user = database.child("boon").child("notes").child("users").child(interaction.user.id).get().val()
                ltuid = user["ltuid"]
                ltoken = user["ltoken"]
                gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
                gameAccounts = await gc.get_game_accounts()
                honkaiUIDs.clear()
                for accounts in gameAccounts:
                    if str(accounts.game_biz) == "bh3_global":
                        honkaiUIDs.append(accounts.uid)

                embed = discord.Embed(title="Already registered but Honkai is not activated", description="You already registered your account, but you haven't activated a Honkai account. Please choose a uid below.", color=3092790)
                await interaction.followup.send(embed=embed, view=SelectAccView())

            elif not database.child("boon").child("notes").child("users").child(interaction.user.id).get().val():
                embed = discord.Embed(title="Please register first", description="Do </register:1056948453118328892>, the uid in the modal is for Genshin. put 0 if you don't want to link your Genshin account.")
        
        except Exception as e:
            print(e)
            
# async def setup(bot):
#     await bot.add_cog(honkaiChronicle(bot))

async def setup(bot):
    await bot.add_cog(honkaiChronicle(bot))