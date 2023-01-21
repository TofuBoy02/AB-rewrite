import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
from discord import app_commands
from discord.ext import commands
import requests
from typing import List
from collections import deque

TOKEN = os.getenv('TOKEN')
RAPIDAPITOKEN = os.getenv("RAPIDAPITOKEN")
url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"

headers = {
	"X-RapidAPI-Key": RAPIDAPITOKEN,
	"X-RapidAPI-Host": "mashape-community-urban-dictionary.p.rapidapi.com"
}

class PaginatorView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__(timeout=30)

        self.embeds = embeds
        self.queue = deque(embeds)

class pages(discord.ui.View):
    def __init__(self, definitions, index, term, authors, examples):
        self.definitions = definitions
        self.length = len(definitions)
        self.index = index
        self.term = term
        self.authors = authors
        self.examples = examples
        super().__init__(timeout=100)

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.blurple, disabled=True)
    async def prevDefinition(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if self.index == 1:
                button.disabled = True
                self.index -= 1
                embed = discord.Embed(title=f"Definition of {self.term}", description=f"**Defintion {self.index + 1} of {self.length}**\n\n{self.definitions[self.index]}\n\n**Example:**\n{self.examples[self.index]}\n\n**Author:**\n{self.authors[self.index]}", color=3092790)
                await interaction.response.edit_message(embed=embed, view=self)
                self.nextDefinition.disabled = False
            elif self.index > 1:
                self.index -= 1
                embed = discord.Embed(title=f"Definition of {self.term}", description=f"**Defintion {self.index + 1} of {self.length}**\n\n{self.definitions[self.index]}\n\n**Example:**\n{self.examples[self.index]}\n\n**Author:**\n{self.authors[self.index]}", color=3092790)
                await interaction.response.edit_message(embed=embed, view=self)
                self.nextDefinition.disabled = False
        except Exception as e:
            self.index = self.index - 1
            print(e)
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def nextDefinition(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if self.index != self.length:
                self.index += 1
                embed = discord.Embed(title=f"Definition of {self.term}", description=f"**Defintion {self.index + 1} of {self.length}**\n\n{self.definitions[self.index]}\n\n**Example:**\n{self.examples[self.index]}\n\n**Author:**\n{self.authors[self.index]}", color=3092790)
                self.prevDefinition.disabled = False
                if self.index + 1 == self.length:
                    button.disabled = True
                await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            self.index = self.index - 1
            print(e)



        


class define(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print ('define cog is online.')

    @app_commands.command(name="define", description="Define a term (urban dictionary)")
    async def define(self, interaction: discord.Interaction, term: str):
        await interaction.response.defer()
        try:
            definitions = []
            authors = []
            examples = []
            
            querystring = {"term": term}
            response = requests.request("GET", url, headers=headers, params=querystring)
            json = response.json()['list']
            for definition in json:
                definitions.append(definition['definition'].replace("[", "").replace("]", ""))
                authors.append(definition['author'])
                examples.append(definition['example'].replace("[", "").replace("]", ""))
        
            index = 0
            length = len(definitions)
            # definition = json['list'][index]['definition']
            # definition = definition.replace("[", "").replace("]", "")
            # author = json['list'][index]['author']

            # print(json)
            embed = discord.Embed(title=f"Definition of {term}", description=f"**Defintion {index + 1} of {length}**\n\n{definitions[0]}\n\n**Example:**\n{examples[index]}\n\n**Author:**\n{authors[0]}", color=3092790)
            if len(definitions) > 1:
                await interaction.followup.send(embed=embed, view=pages(definitions = definitions, index=index, term = term, authors = authors, examples = examples))
            else:
                await interaction.followup.send(embed=embed)
        except Exception as e:
            print(e)
            embed = discord.Embed(title="Error", description="Definition not found.")
            await interaction.followup.send(embed=embed)
        
        
            
async def setup(bot):
    await bot.add_cog(define(bot))

# async def setup(bot):
#     await bot.add_cog(define(bot), guilds=[discord.Object(id=980092176488886383)])