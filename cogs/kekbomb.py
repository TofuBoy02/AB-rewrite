import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import asyncio
from discord import app_commands

TOKEN = os.getenv('TOKEN')



class kekbomb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kekbomb_ctx = app_commands.ContextMenu(
            name='kekbomb this message',
            callback=self.kekbomb_func, # set the callback of the context menu to "my_cool_context_menu"
        )
        self.bot.tree.add_command(self.kekbomb_ctx)
        

    async def kekbomb_func(self, interaction: discord.Interaction, message: discord.Message):
        try:
            await interaction.response.defer(ephemeral=True)
            await message.add_reaction("<:KEKW:991376170409001070>")
            await asyncio.sleep(0.2)
            await message.add_reaction("<:kekw:1008348037543907340>")
            await asyncio.sleep(0.2)
            await message.add_reaction("<:KEKW:1059065452480974878>")
            await asyncio.sleep(0.2)
            await message.add_reaction("<:KEKW2:1059065474018721842>")
            await asyncio.sleep(0.2)
            await message.add_reaction("<:KEKW3:1059065503894749269>")
            await asyncio.sleep(0.2)
            await message.add_reaction("<:KEKW4:1059065529257697291>")
            await asyncio.sleep(0.2)
            await message.add_reaction("<:KEKW5:1059065556130598922>")
            await asyncio.sleep(0.2)
            await interaction.followup.send("Successfully kekbombed the message", ephemeral=True)
        except Exception as e:
            print(e)
        
            

async def setup(bot):
    await bot.add_cog(kekbomb(bot))

# async def setup(bot):
    # await bot.add_cog(kekbomb(bot), guilds=[discord.Object(id=980092176488886383)])