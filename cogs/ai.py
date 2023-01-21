import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
# import openai
import json
import requests

load_dotenv()

TOKEN = os.getenv('TOKEN')




class ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ai cog is online.")

    @commands.Cog.listener()
    async def on_message(self,ctx):
        if ctx.author.id == 1007934486815723520:
            return

        elif ctx.content.startswith('b.'):
            print("test")
            prompt_msg = str(ctx.content)[3:]

        elif not ctx.content.startswith('b.'):
            return

        if prompt_msg ==None:
            await ctx.reply("Please send a message~")

        elif prompt_msg != None:
            message = await ctx.reply("Thinking...")
            response = requests.get(f"https://tofuboy.pythonanywhere.com/albedo?query={prompt_msg}", verify=False)
            response = response.json()['text']
            await message.edit(content=response)

        reference = ctx.reference
        if reference is None:
            return
        elif ctx.reference.resolved.author.id == 1007934486815723520:
            message = await ctx.reply("Thinking...")
            prompt_msg = str(ctx.content)
            response = requests.get(f"https://tofuboy.pythonanywhere.com/albedo?query={prompt_msg}", verify=False)
            response = response.json()['text']
            await message.edit(content=response)
        
async def setup(bot):
    await bot.add_cog(ai(bot))
