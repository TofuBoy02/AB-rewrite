import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
from discord import app_commands
from discord.ext import commands
import time
from datetime import date
from humanfriendly import format_timespan
import pytz
from datetime import datetime

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


class playtimeStat(commands.GroupCog, name="playtime"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print ('playtime cog is online.')

    @app_commands.command(name="today", description="Check how much time you've spent on Genshin today")
    async def playtimeToday(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            #if user has set a timezone:
            if database.child("boon").child("playtime").child(interaction.user.id).child("settings").child("timezone").shallow().get().val():
                user_tz = database.child("boon").child("playtime").child(interaction.user.id).child("settings").child("timezone").get().val()
                tz = pytz.timezone(user_tz)
                date_now = datetime.now(tz=tz)
                year = date_now.strftime('%Y')
                month = date_now.strftime("%m")
                day = date_now.strftime("%d")
                date_today = datetime(int(year), int(month), int(day), 0, 0, 0)
                date_today_last = datetime(int(year), int(month), int(day), 23, 59, 59)
                date_today_unix = int(time.mktime(date_today.timetuple()))
                date_today_last_unix = int(time.mktime(date_today_last.timetuple()))

                sessions_today = database.child("boon").child("playtime").child(interaction.user.id).child(year).child(month).shallow().get().val()
                durations = []
                session_data = database.child("boon").child("playtime").child(interaction.user.id).child(year).child(month).get().val()
                for session in sessions_today:
                    if int(session) >= date_today_unix and int(session) <= date_today_last_unix:
                        durations.append(session_data[session]["Duration"])
                if durations:
                    total_duration = sum(durations)
                    humanfriendly = format_timespan(total_duration, max_units=2)
                    embed = discord.Embed(title=f"{interaction.user.name}'s Genshin play time today", description=f"{humanfriendly}", color=3092790)
                    await interaction.followup.send(embed=embed)
                elif not durations:
                    embed = discord.Embed(title="Error", description=f"You have not played Genshin today.\n\nReminder: This only records your playtime if \"Genshin Impact\" is displayed on your Discord rich presence or **Playing** status. Unfortunately this only works properly if you play on pc.", color=3092790)
                    embed.set_image(url="https://media.discordapp.net/attachments/1008333194271129600/1058764636519927808/image.png")
                    await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title="Please set up a timezone", description=("Use /set timezone [GMT/UTC Offset]. Or you can use </playtime thismonth:1057666922587639858> or </playtime thisyear:1057666922587639858> if you don't want to set up a timezone."), color=3092790)
                await interaction.followup.send(embed = embed)
        except Exception as e:
            print(e)

    @app_commands.command(name="thismonth", description="Check how much time you've spent on Genshin this month!")
    async def playtimeThisMonth(self, interaction: discord.Interaction):
        try:
            year = datetime.now().strftime('%Y')
            month = datetime.now().strftime("%m")
            day = datetime.now().strftime("%d")
            # try:
            #     total = database.child("boon").child("playtime").child(interaction.user.id).child(year).child(month).child("total").get().val()
            #     humanfriendly = format_timespan(total, max_units=2)
            #     embed = discord.Embed(title=f"{interaction.user.name}'s Genshin play time this month", description=f"{humanfriendly}", color=3092790)
            #     await interaction.response.send_message(embed=embed)
            # except:
            #     embed = discord.Embed(title="Error", description="You have not played Genshin this month. Keep it up!", color=3092790)
                # await interaction.response.send_message(embed=embed)
            try:
                sessions_this_month = database.child("boon").child("playtime").child(interaction.user.id).child(year).child(month).get().val()
                durations = []
                for session in sessions_this_month:
                    durations.append(sessions_this_month[session]["Duration"])
                total_duration = sum(durations)
                humanfriendly = format_timespan(total_duration, max_units=2)
                embed = discord.Embed(title=f"{interaction.user.name}'s Genshin play time this month", description=f"{humanfriendly}", color=3092790)
                await interaction.response.send_message(embed=embed)
            except:
                embed = discord.Embed(title="Error", description="You have not played Genshin this month. Keep it up!\n\nReminder: This only records your playtime if \"Genshin Impact\" is displayed on your Discord rich presence or **Playing** status. Unfortunately this only works properly if you play on pc.", color=3092790)
                embed.set_image(url="https://media.discordapp.net/attachments/1008333194271129600/1058764636519927808/image.png")
                await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(e)

    @app_commands.command(name="yesterday", description="Check how much time you've spent on Genshin yesterday!")
    async def playtimeYesterday(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            #if user has set a timezone:
            if database.child("boon").child("playtime").child(interaction.user.id).child("settings").child("timezone").shallow().get().val():
                user_tz = database.child("boon").child("playtime").child(interaction.user.id).child("settings").child("timezone").get().val()
                tz = pytz.timezone(user_tz)
                date_now = datetime.now(tz=tz)
                year = date_now.strftime('%Y')
                month = date_now.strftime("%m")
                day = date_now.strftime("%d")
                date_today = datetime(int(year), int(month), int(day) - 1, 0, 0, 0)
                date_today_last = datetime(int(year), int(month), int(day) - 1, 23, 59, 59)
                date_today_unix = int(time.mktime(date_today.timetuple()))
                date_today_last_unix = int(time.mktime(date_today_last.timetuple()))

                sessions_today = database.child("boon").child("playtime").child(interaction.user.id).child(year).child(month).shallow().get().val()
                durations = []
                session_data = database.child("boon").child("playtime").child(interaction.user.id).child(year).child(month).get().val()
                for session in sessions_today:
                    if int(session) >= date_today_unix and int(session) <= date_today_last_unix:
                        durations.append(session_data[session]["Duration"])
                if durations:
                    total_duration = sum(durations)
                    humanfriendly = format_timespan(total_duration, max_units=2)
                    embed = discord.Embed(f"{interaction.user.name}'s Genshin play time yesterday", description=f"{humanfriendly}", color=3092790)
                    await interaction.followup.send(embed=embed)
                elif not durations:
                    embed = discord.Embed(title="Error", description="You did not play Genshin yesterday.", color=3092790)
                    await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title="Please set up a timezone", description=("Use /set timezone [GMT/UTC Offset]. Or you can use </playtime thismonth:1057666922587639858> or </playtime thisyear:1057666922587639858> if you don't want to set up a timezone."), color=3092790)
                await interaction.followup.send(embed = embed)
        except Exception as e:
            print(e)

    @app_commands.command(name="thisyear", description="Check how much time you've spent on Genshin this month!")
    async def playtimeThisYear(self, interaction: discord.Interaction):
        try:
            year = datetime.now().strftime('%Y')
            month = datetime.now().strftime("%m")
            day = datetime.now().strftime("%d")
            # try:
            #     total = database.child("boon").child("playtime").child(interaction.user.id).child(year).child("total").get().val()
            #     humanfriendly = format_timespan(total, max_units=2)
            #     embed = discord.Embed(title=f"{interaction.user.name}'s Genshin play time this year", description=f"{humanfriendly}", color=3092790)
            #     await interaction.response.send_message(embed=embed)
            # except:
            #     embed = discord.Embed(title="Error", description="You have not played Genshin this year. Keep it up!", color=3092790)
            #     await interaction.response.send_message(embed=embed)
            #     return
            try:
                sessions_this_year = database.child("boon").child("playtime").child(interaction.user.id).child(year).get().val()
                durations = []
                for month in sessions_this_year:
                    sessions_this_month = database.child("boon").child("playtime").child(interaction.user.id).child(year).child(month).get().val()
                    for session in sessions_this_month:
                        durations.append(sessions_this_month[session]["Duration"])
                total_duration = sum(durations)
                humanfriendly = format_timespan(total_duration, max_units=2)
                embed = discord.Embed(title=f"{interaction.user.name}'s Genshin play time this year", description=f"{humanfriendly}", color=3092790)
                await interaction.response.send_message(embed=embed)
            except:
                embed = discord.Embed(title="Error", description="You have not played Genshin this year. Keep it up!\n\nReminder: This only records your playtime if \"Genshin Impact\" is displayed on your Discord rich presence or **Playing** status. Unfortunately this only works properly if you play on pc.", color=3092790)
                embed.set_image(url="https://media.discordapp.net/attachments/1008333194271129600/1058764636519927808/image.png")
                await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(e)

# async def setup(bot):
#     await bot.add_cog(playtimeStat(bot))

async def setup(bot):
    await bot.add_cog(playtimeStat(bot), guilds=[discord.Object(id=991361510263767080)])