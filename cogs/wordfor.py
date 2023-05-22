import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
from discord import app_commands
from discord.ext import commands
import requests
import traceback

TOKEN = os.getenv('TOKEN')


class wordforClass(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print ('Wordfor cog is online.')

    def clean_query(query: str) -> str:
        query = query.lower()  # convert all characters to lowercase
        query = query.replace(" ", "+")  # replace spaces with +
          
        return query


    @app_commands.command(name="wordfor", description="Find the word by describing it!")
    async def wordfor(self, interaction: discord.Interaction, description:str):
        await interaction.response.defer()
        try:
            query = wordforClass.clean_query(description)
            print(f"Query: {query}")
            url =f"https://api.datamuse.com/words?ml={query}"

            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                words = ""
                index = 5
                for i, item in enumerate(data):
                    print(item['word'])
                    if i == 10:  # stop after 5 iterations
                        break
                    words += f"\n- {item['word']}"
                    index -= 1

                embed = discord.Embed(title=description, description=words, color=3092790)
                await interaction.followup.send(embed=embed)
                
            else:
                embed = discord.Embed(title="Error", description=f"Error making request. Status code: {response.status_code}", color=3092790)
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(e)
            traceback.print_exc()

            
async def setup(bot):
    await bot.add_cog(wordforClass(bot))

# async def setup(bot):
#     await bot.add_cog(wordforClass(bot), guilds=[discord.Object(id=1007935142779703406)])
