import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
from discord import app_commands
from translate import Translator

TOKEN = os.getenv('TOKEN')


class translateContext(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pt_context_month = app_commands.ContextMenu(
            name='Translate to English',
            callback=self.translate_context,
        )
        self.bot.tree.add_command(self.pt_context_month)
        

    async def translate_context(self, interaction: discord.Interaction, message: discord.Message):
        try:
            translator = Translator(to_lang="en", from_lang="autodetect")
            translation = translator.translate(message.content)
            embed = discord.Embed(title="Translation", description=f"{translation}\n\n**Original:**\n{message.content}", color=3092790)
            embed2 = discord.Embed(title = f"{interaction.user.name} used Translate", description=f"**In:** {interaction.guild.name}\n\n**Message by:** {message.author.name}\n\n**Message:**\n{message.content}\n\n**Translation:**\n{translation}", color=3092790)
            await interaction.response.send_message(embed=embed)
            channel = self.bot.get_channel(1008333194271129600)
            await channel.send(embed=embed2)

        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(translateContext(bot))