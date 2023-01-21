import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import pyrebase
import random
from collections import Counter
import asyncio
import time
import datetime
from humanfriendly import format_timespan

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

# Rarity Index Fetcher

rarity_3_index = len(database.child("cards").child("rarity-3").get().val())
rarity_4_index = len(database.child("cards").child("rarity-4").get().val())
rarity_5_index = len(database.child("cards").child("rarity-5").get().val())

status_claimed = {"status": "claimed",
                  "timestamp": f"{int(time.time()) + 1800}"}
status_can_claim = {"status": "can_claim"}


class buyPullModal(discord.ui.Modal, title="Buy Pulls"):
    amount: int = discord.ui.TextInput(label = "How much?", placeholder="amount", style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            intamout = int(self.amount.value)
            user_bal = database.child("users").child(interaction.user.id).child("currency").get().val()
            if intamout != 0:
                    if user_bal >= intamout*10:
                        database.child("users").child(interaction.user.id).update({"currency": user_bal-(intamout*10)})
                        current_pulls = database.child("users").child(interaction.user.id).child("pulls").child("amount").get().val()
                        database.child("users").child(interaction.user.id).child("pulls").update({"amount": current_pulls+intamout})
                        await interaction.response.send_message(f"added {intamout} pulls to your account.")
        except Exception as e:
            print(e)


class buttonBuyPull(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=100)
    
    @discord.ui.button(label="Buy more Pulls", style=discord.ButtonStyle.green, emoji="🛒")
    async def registerbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(buyPullModal())

class buttonBuyClaim(discord.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__(timeout=100)
    
    @discord.ui.button(label="Buy Claim", style=discord.ButtonStyle.green, emoji="💵")
    async def registerbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:

            if interaction.user.id == self.author:

                user_bal = database.child("users").child(interaction.user.id).child("currency").get().val()

                if user_bal > 500 or user_bal == 500:
                    new_bal = user_bal - 500
                    await interaction.response.send_message(f"<@{interaction.user.id}> You can now claim. Your new balance is <:cecilia:1038333000905134141> {new_bal}")
                    database.child("users").child(interaction.user.id).update({"claim_time": 1})
                    database.child("users").child(interaction.user.id).update({"currency": new_bal})

                elif user_bal < 500:
                    await interaction.response.send_message(f"<@{interaction.user.id}> You don't have enough <:cecilia:1038333000905134141> to buy \"claim\"")
            else:
                await interaction.response.send_message(f"<@{interaction.user.id}> this is not yours!", ephemeral=True)
        except Exception as e:
            print(e)


class gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("gacha cog is online.")

    @commands.command()
    async def g(self, ctx):
        
        try:
            user_pull_data = database.child('users').child(ctx.author.id).child('pulls').get().val()
            if user_pull_data['amount'] > 0:
                database.child('users').child(ctx.author.id).child('pulls').update({"amount": user_pull_data['amount']-1})
            elif user_pull_data['amount'] <= 0:
                time_remaining = database.child('pull_refresh').child('unix').get().val()
                time_remaining = time_remaining - int(time.time())
                await ctx.reply(f"You have used up all your pulls! You will get {user_pull_data['speed']} pulls in {format_timespan(time_remaining)} seconds.", view=buttonBuyPull())
                return
        except:
            user_pull_data = {"amount": 4, "speed": 5, "max": 5}
            database.child('users').child(ctx.author.id).child('pulls').set(user_pull_data)

        rarities = ["rarity-3", "rarity-4", "rarity-5"]
        chance = [50, 44, 6]

        # DEFINES FINAL ROLLED RARITY
        result = random.choices(rarities, chance, k=1)
        counter_res = (Counter(result))

        final_rarity = list(counter_res.keys())[
            list(counter_res.values()).index(1)]


        if final_rarity == "rarity-3":
            rarity_cecilia = 20
            card_index = rarity_3_index - 1
            rarity_stars = "⭐⭐⭐"
        elif final_rarity == "rarity-4":
            rarity_cecilia = 100
            card_index = rarity_4_index - 1
            rarity_stars = "⭐⭐⭐⭐"
        elif final_rarity == "rarity-5":
            rarity_cecilia = 500
            card_index = rarity_5_index - 1
            rarity_stars = "⭐⭐⭐⭐⭐"


        # DEFINES THE FINAL CARD
        random_card_index = random.randint(1, card_index)

        # FETCH THE CARD DATA
        card_data = database.child("cards").child(
            f"{final_rarity}").child(random_card_index).get().val()

        # DEFINE DATA OF STORED CARDS OF USER WHEN CLAIMED
        claimed_card_data = {"Card_name": f"{card_data['card_name']}",
                             "Card_ID": f"{final_rarity}-{random_card_index}",
                             "Card_rarity": f"{card_data['rarity']}"}

        # DEFINE UNIX TIMES
        current_unix = int(time.time())
        current_unix_added = current_unix + 3600
        current_unix_added_cecilia = current_unix + 600

        # CHECK IF CARD IS CLAIMED
        if card_data['claimed'] == "true" or card_data['claimed'] == True:
            card_is_claimed = True
        else:
            card_is_claimed = False

        if card_data['description'] == "None":
            description = ""
        else:
            description = f"{card_data['description']}\n"

        # DEFINE THE CARD EMBED
        embed = discord.Embed(title=f"Art by {card_data['artist']}", color=discord.Color.random(
        ), description=f"**{card_data['card_name']}**\n{rarity_stars}\n{description}[Link]({card_data['post_link']})")
        embed.set_image(url=card_data['image'])

        # ADD FOOTER IF CARD IS CLAIMED BY SOMEONE ELSE ALREADY
        if card_is_claimed:
            owner: int = database.child("cards").child(f"{final_rarity}").child(
                random_card_index).child("owned_by").get().val()

            # try:
            uid_to_user = await self.bot.fetch_user(owner)
            uid_to_user = str(uid_to_user)[:-5]
            
            # except:
            #   uid_to_user = "Error"
            embed.set_footer(
                text=f"Owned by {uid_to_user}. Claim to get {rarity_cecilia} cecilia.")

        # SENDS THE EMBED
        message = await ctx.reply(embed=embed)

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: reaction.message == message,
                    timeout=20
                )

                # CLAIM EVENT

                if not database.child("users").child(user.id).child("claim_time").get().val():

                    if not card_is_claimed:
                        await message.edit(content="", embed=embed.set_footer(text=f"Claimed by {user.name}"))
                        database.child("users").child(user.id).update({"currency": 0})
                        database.child("users").child(user.id).update({"username": user.name})
                        database.child("users").child(user.id).child("owned_cards").child(card_data['card_name']).update(claimed_card_data)
                        database.child("users").child(user.id).update({"claim_time": current_unix_added})
                        database.child("cards").child(f"{final_rarity}").child(random_card_index).update({"claimed": "true"})
                        database.child("cards").child(f"{final_rarity}").child(random_card_index).update({"owned_by": user.id})
                        return

                    if card_is_claimed:

                        await message.edit(content="", embed=embed.set_footer(text=f"Added {rarity_cecilia} Cecilia for {user.name}"))
                        database.child("users").child(user.id).update({"username": user.name})
                        database.child("users").child(user.id).update({"currency": rarity_cecilia})
                        database.child("users").child(user.id).update({"claim_time": current_unix_added_cecilia})
                        return

                elif database.child("users").child(user.id).shallow().get().val():
                    saved_unix = database.child("users").child(
                        user.id).child("claim_time").get().val()

                    if current_unix > saved_unix:

                        if not card_is_claimed:
                            await message.edit(content="", embed=embed.set_footer(text=f"Claimed by {user.name}"))
                            database.child("users").child(user.id).child("owned_cards").child(card_data['card_name']).update(claimed_card_data)
                            database.child("users").child(user.id).update({"claim_time": current_unix_added})
                            database.child("cards").child(f"{final_rarity}").child(random_card_index).update({"claimed": "true"})
                            database.child("cards").child(f"{final_rarity}").child(random_card_index).update({"owned_by": user.id})
                            database.child("users").child(user.id).update({"username": user.name})
                            return

                        elif card_is_claimed:
                            await message.edit(content="", embed=embed.set_footer(text=f"Added {rarity_cecilia} Cecilia for {user.name}"))
                            current_balance = database.child("users").child(user.id).child("currency").get().val()
                            database.child("users").child(user.id).update({"currency": current_balance + rarity_cecilia})
                            database.child("users").child(user.id).update({"claim_time": current_unix_added_cecilia})
                            database.child("users").child(user.id).update({"username": user.name})
                            return

                    if current_unix < saved_unix:
                        unix_difference = saved_unix - current_unix
                        converted = time.strftime(
                            "%Mm%Ss", time.gmtime(unix_difference))
                        await ctx.reply(f"You have alread claimed a card. Try again in {converted}", view=buttonBuyClaim(author=ctx.author.id))

            except asyncio.TimeoutError:
                return
            except Exception as e:
                print(e)

async def setup(bot):
    await bot.add_cog(gacha(bot))