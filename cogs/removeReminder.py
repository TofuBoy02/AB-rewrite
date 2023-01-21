import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
from discord import app_commands
from discord.ext import commands

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


class removeReminder(commands.GroupCog, name="cancel"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print ('Sync cog is online.')

    @app_commands.command(name="reminder", description="Cancels your resin reminder.")
    async def cancelReminder(self, interaction: discord.Interaction):
        if not database.child("boon").child("notes").child("reminders").child(interaction.user.id).get().val():
            await interaction.response.send_message("You do not have a resin reminder set.")
        else:
            await interaction.response.send_message("Successfully cancelled your resin reminder.")
            database.child("boon").child("notes").child("reminders").child(interaction.user.id).remove()
            
async def setup(bot):
    await bot.add_cog(removeReminder(bot))

# async def setup(bot):
#     await bot.add_cog(removeReminder(bot), guilds=[discord.Object(id=980092176488886383)])