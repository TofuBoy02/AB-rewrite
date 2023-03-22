import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
from humanfriendly import format_timespan
import genshin
import datetime

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

class readjustBtn(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=100)
        self.user = user
    @discord.ui.button(label="Do not readjust", style=discord.ButtonStyle.blurple)
    async def readjust(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(color=3092790, title="Success", description="Reminder will be deleted quietly if resin is used.")
        database.child('boon').child('notes').child('reminders').child(self.user).update({"adjust": False})
        await interaction.response.edit_message(embed=embed, view=None)


class ResinRemindSpec(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Specific Resin Count Reminder cog is online.")

    async def get_resin(author):
        try:
            user_data = database.child("boon").child("notes").child("users").child(author).get().val()
            ltoken = user_data["ltoken"]
            ltuid = user_data["ltuid"]
            uid = user_data["uid"]
            gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
            notes = await gc.get_genshin_notes(uid)
            resin_now = notes.current_resin
            max_resin = notes.max_resin

            return {"resin_now": resin_now, "max": max_resin}
        except Exception as e:
            print(e)

    @commands.command()
    async def rr(self,ctx, resin):
        try:
            if int(resin) > 160:
                await ctx.reply("pls get help the max is 160")
                return
            resin = int(resin)
            resin_data = await ResinRemindSpec.get_resin(author=ctx.author.id)
            if resin <= resin_data["resin_now"]:
                embed = discord.Embed(description=f"You have more resin than the target resin amount.\n<:resin:950411358569136178> {resin_data['resin_now']}/{resin_data['max']}", color=3092790)
                await ctx.send(embed=embed)
            elif resin > resin_data["resin_now"]:
                remaining_resin = resin - resin_data["resin_now"]
                time_left = remaining_resin * 8
                seconds_left = time_left * 60
                time_now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                reminder_time = time_now + seconds_left
                data = {"channel": str(ctx.channel.id),
                        "time": reminder_time,
                        "specific": True,
                        "target": int(resin),
                        "adjust": True}

                if database.child("boon").child("notes").child("reminders").child(ctx.author.id).get().val():
                    embed = discord.Embed(description="You already have a reminder, please clear it with </cancel reminder:1059393572878680066>", color=3092790)
                    await ctx.reply(embed=embed)
                else:
                    database.child("boon").child("notes").child("reminders").child(ctx.author.id).update(data)
                    embed = discord.Embed(description=f"Okay, I will remind you in **{format_timespan(seconds_left)}**\nCurrent <:resin:950411358569136178>:  {resin_data['resin_now']}/{resin_data['max']}\n\nTimer will readjust if you use your resin, if you want the timer to quietly delete itself if you use your resin, click the red button.", color=3092790)
                    await ctx.reply(embed=embed, view=readjustBtn(user=ctx.author.id))
            
        except Exception as e:
            print(e)
            await ctx.reply(f"Please make sure to input a number after `.rr`")
        
        
async def setup(bot):
    await bot.add_cog(ResinRemindSpec(bot))