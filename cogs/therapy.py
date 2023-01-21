import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import asyncio
from discord import app_commands

TOKEN = os.getenv('TOKEN')



class therapy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.therapy_ctx = app_commands.ContextMenu(
            name='Therapy',
            callback=self.therapy_func, # set the callback of the context menu to "my_cool_context_menu"
        )
        self.bot.tree.add_command(self.therapy_ctx)
        

    async def therapy_func(self, interaction: discord.Interaction, message: discord.Message):
        try:
            embed = discord.Embed(title="Message", description=message.content, color=3092790)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar)
            if message.attachments:
                embed.set_image(url=message.attachments[0].url)
            await interaction.response.send_message(f"Okay! I've submitted a ticket to https://etherapypro.com/ with this message attached. I'll message <@{message.author.id}> when an agent is available.", embed=embed)

        except Exception as e:
            print(e)
        
            

async def setup(bot):
    # await bot.add_cog(therapy(bot))

# async def setup(bot):
    await bot.add_cog(therapy(bot))