import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import asyncio
from discord import app_commands

TOKEN = os.getenv('TOKEN')



class star(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.star_ctx = app_commands.ContextMenu(
            name='Star this message',
            callback=self.star_func, # set the callback of the context menu to "my_cool_context_menu"
        )
        self.bot.tree.add_command(self.star_ctx)
        

    async def star_func(self, interaction: discord.Interaction, message: discord.Message):
        try:
            await message.add_reaction("⭐")
            await interaction.response.send_message("Successfully starred the message", ephemeral=True)
        except Exception as e:
            print(e)
        
            

async def setup(bot):
    await bot.add_cog(star(bot))

# async def setup(bot):
    # await bot.add_cog(star(bot), guilds=[discord.Object(id=980092176488886383)])