import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
from humanfriendly import format_timespan
from collections import OrderedDict

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

class ChestSelect(discord.ui.Select):
    def __init__(self, data):
        self.data = data
        option_list = [
        discord.SelectOption(label="Common Chest", emoji="<:common_chest:1037649653145030697>"),
        discord.SelectOption(label="Exquisite Chest", emoji="<:exquisite_chest:1037649650645217341>"),
        discord.SelectOption(label="Precious Chest", emoji="<:precious_chest:1037649648602591362>"),
        discord.SelectOption(label="Luxurious Chest", emoji="<:Luxurious_chest:1037649646677401660>"),
        discord.SelectOption(label="Remarkable Chest", emoji="<:remarkable_chest:1037649644748029994>"),
        discord.SelectOption(label="Total Chests")
        ]

        super().__init__(placeholder="Chest Type", max_values=1, min_values=1, options=option_list)
    
    def compute_rank(data, chest_type, title):
        try:
            sorted_data = OrderedDict(sorted(data.items(), key=lambda x: x[1][chest_type], reverse=True))
            users = ''
            rank = 1
            for user in sorted_data:
                users += (f"#{rank}: <@{user}> ({data[user][chest_type]}) \n")
                rank += 1
            embed = discord.Embed(title=title, description=f"{users}\n\n*Data is indexed every 10 hours*\nUpdate yours using `.n`", color=3092790)
            return embed
        except Exception as e:
            print(f"Exception at compute_rank: {e}")
    async def callback(self, interaction: discord.Interaction):
        try:
            if self.values[0] == "Common Chest":
                chest_type = "common_chest"
                title = "<:common_chest:1037649653145030697> Common Chest Leaderboard"
            elif self.values[0] == "Exquisite Chest":
                chest_type = "exquisite_chest"
                title = "<:exquisite_chest:1037649650645217341> Exquisite Chest Leaderboard"
            elif self.values[0] == "Precious Chest":
                chest_type = "precious_chest"
                title = "<:precious_chest:1037649648602591362> Precious Chest Leaderboard"
            elif self.values[0] == "Luxurious Chest":
                chest_type = "luxurious_chest"
                title = "<:Luxurious_chest:1037649646677401660> Luxurious Chest Leaderboard"
            elif self.values[0] == "Remarkable Chest":
                chest_type = "remarkable_chest"
                title = "<:remarkable_chest:1037649644748029994> Remarkable Chest Leaderboard"
            elif self.values[0] == "Total Chests":
                chest_type = "total_chest"
                title = "<:Luxurious_chest:1037649646677401660> Total Chest Leaderboard"
            embed = ChestSelect.compute_rank(data = self.data, chest_type=chest_type, title = title)
            await interaction.response.edit_message(embed=embed)

        except Exception as e:
            print(f"Exception at select: {e}")

class ChestSelectView(discord.ui.View):
    def __init__(self, *, timeout=100, data):
        super().__init__(timeout=timeout)
        self.add_item(ChestSelect(data = data))


class chestlb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("chest lb cog is online.")


    @commands.command()
    async def chestlb(self,ctx):
        try:
            data = database.child("boon").child("notes").child("lb").get().val()
            sorted_data = OrderedDict(sorted(data.items(), key=lambda x: x[1]['total_chest'], reverse=True))
            users = ''
            rank = 1
            for user in sorted_data:
                users += (f"#{rank}: <@{user}> ({data[user]['total_chest']}) \n")
                rank += 1
            
            
            embed = discord.Embed(title="<:Luxurious_chest:1037649646677401660> Chest Leaderboard", description=f"{users}\n\n*Data is indexed every 10 hours*\nUpdate yours using `.n`", color=3092790)
            await ctx.reply(embed=embed, view=ChestSelectView(data = data))

                
        except Exception as e:
            await ctx.reply(f"An error occured.\n`{e}`")
        
        
async def setup(bot):
    await bot.add_cog(chestlb(bot))