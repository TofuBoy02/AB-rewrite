import os, sys
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

class SameAccountButtonTryAgain(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=100)
    
    @discord.ui.button(label="Try again", style=discord.ButtonStyle.blurple)
    async def registerbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(registerAltModal())

class uidSelect(discord.ui.Select):
    def __init__(self, altname, ltoken, ltuid, cookie, genshinUIDs):
        self.altname = altname
        self.ltoken = ltoken
        self.ltuid = ltuid
        self.cookie = cookie
        self.genshinUIDs = genshinUIDs
        option_list = []
        if genshinUIDs:
            for uid in genshinUIDs:
                option_list.append(discord.SelectOption(label=f"{uid}"))
        elif not genshinUIDs:
            option_list.append(discord.SelectOption(label=f"You have no Genshin Accounts"))
        options = option_list
        super().__init__(placeholder="Select a Genshin UID", max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "You have no Genshin Accounts":
            await interaction.response.send_message("Stop trying bitch", ephemeral=True)
            return
        else:
            await interaction.response.defer(ephemeral=True)
            data = {"ltoken": self.ltoken, "ltuid": int(self.ltuid), "cookie_token": self.cookie, "uid": int(self.values[0])}
            database.child("boon").child("notes").child("users").child(interaction.user.id).child("alts").child(self.altname).update(data)
            database.child("boon").child("notes").child("users").child(interaction.user.id).update(data)
            await interaction.followup.send(content = f"Successfully set your Genshin UID to {self.values[0]}. Your Daily check-in for Genshin will be automatically be claimed, and you can check your resin amount using `.n`", ephemeral=True)

class uidSelectView(discord.ui.View):
    def __init__(self, *, timeout=100, altname, ltoken, ltuid, cookie, genshinUIDs):
        super().__init__(timeout=timeout)
        self.add_item(uidSelect(altname, ltoken, ltuid, cookie, genshinUIDs))


class registerAltModal(discord.ui.Modal, title="Registration"):
    altname = discord.ui.TextInput(label = "Alt name", placeholder="Sample: a", style=discord.TextStyle.short, max_length=5, min_length=1)
    ltoken = discord.ui.TextInput(label = "Paste ltoken here", placeholder="ltoken=XXXXXXX;", style=discord.TextStyle.short)
    ltuid = discord.ui.TextInput(label = "Paste ltuid here", placeholder="ltuid=12345;", style=discord.TextStyle.short)
    cookie = discord.ui.TextInput(label = "Paste cookie_token here", placeholder="cookie_token=XXXXXX;", style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Getting your accounts... Please wait.", ephemeral=True)
        try:
            genshinUIDs = []
            gc = genshin.Client({"ltoken": self.ltoken.value[7:-1], "ltuid": self.ltuid.value[6:-1]})
            gameAccounts = await gc.get_game_accounts()
            for accounts in gameAccounts:
                if str(accounts.game_biz) == "hk4e_global":
                    genshinUIDs.append(accounts.uid)
            await interaction.edit_original_response(content="Please choose a UID", view=uidSelectView(altname = self.altname.value, ltoken = self.ltoken.value[7:-1], ltuid = self.ltuid.value[6:-1], cookie = self.cookie.value[13:-1], genshinUIDs = genshinUIDs))


        except Exception as e:
            print(e)
            embed = discord.Embed(title="Error", description="Something went wrong. Please make sure you input the correct information", color=3092790)
            await interaction.edit_original_response(content="", embed=embed, view=SameAccountButtonTryAgain())


class registerAlt(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print ('Registeralt cog is online.')


    @app_commands.command(name="registeralt", description="Register for autoclaim and live notes")
    async def registerAlt(self, interaction: discord.Interaction):
        try:
            if not database.child("boon").child("notes").child("users").child(interaction.user.id).get().val():
                embed = discord.Embed(title="Error", description="You don't have a main account registered. Please register normally using </register:1056948453118328892> instead.", color=3092790)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_modal(registerAltModal())
        except Exception as e:
            print(e)
            
# async def setup(bot):
#     await bot.add_cog(registerAlt(bot))

async def setup(bot):
    await bot.add_cog(registerAlt(bot), guilds=[discord.Object(id=980092176488886383)])