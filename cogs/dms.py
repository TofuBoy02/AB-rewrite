import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import traceback

load_dotenv()

TOKEN = os.getenv('TOKEN')
# openai.api_key = os.getenv("OPENAITOKEN")
url = "https://api.openai.com/v1/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.getenv("OPENAITOKEN")
}




class dmForward(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("DM forwarding cog is online.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            target_channel_id = 1108733494504472697
            target_channel = self.bot.get_channel(target_channel_id)
            if target_channel:
                content = f"**{message.author}:** {message.content}"
                await target_channel.send(content)

            
        
        
async def setup(bot):
    await bot.add_cog(dmForward(bot))