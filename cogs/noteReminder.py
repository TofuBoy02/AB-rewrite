import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
import pyrebase
TOKEN = os.getenv('TOKEN')
import time
import genshin
from humanfriendly import format_timespan, parse_timespan

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


class resinReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.resinReminderCheck.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("pulladd cog is online.")

    @tasks.loop(minutes=1)
    async def resinReminderCheck(self):
        
        print("looping through resin reminders")
        all_reminders = database.child("boon").child("notes").child("reminders").shallow().get().val()
        if all_reminders:
            for reminder in all_reminders:
                try:
                    channel_id = database.child("boon").child("notes").child("reminders").child(reminder).child("channel").get().val()
                    channel = self.bot.get_channel(channel_id)
                    remind_time = database.child("boon").child("notes").child("reminders").child(reminder).child("time").get().val()
                    current_time = int(time.time())

                    if current_time >= remind_time:
                        #CHECK USER'S RESIN IF CAPPED
                        user_data = database.child("boon").child("notes").child("users").child(reminder).get().val()

                        ltoken = user_data["ltoken"]
                        ltuid = user_data["ltuid"]
                        uid = user_data["uid"]

                        gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
                        notes = await gc.get_genshin_notes(uid)
                        current_resin = notes.current_resin
                        max_resin = notes.max_resin
                        uid_to_user = await self.bot.fetch_user(int(reminder))
                        uid_to_user = str(uid_to_user)[:-5]
                        unix_resin = notes.remaining_resin_recovery_time.seconds
                        resin_remaining_time = format_timespan(unix_resin - 600, max_units=2)
                        if current_resin >= 158:
                            
                            embed = discord.Embed(title=f"{uid_to_user}'s Resin Status", description=f"<:resin:950411358569136178> {current_resin}/{max_resin}", color=3092790)

                            await channel.send(f"<@{reminder}>! Your resin is almost capped!", embed=embed)
                            database.child("boon").child("notes").child("reminders").child(reminder).remove()
                        elif current_resin < 158:
                            embed = discord.Embed(title=f"Readjusting {uid_to_user}'s Reminder", description=f"{uid_to_user} asked to be reminded when their resin is almost capped, their resin should almost be capped now, but I checked again and it seems that they've used their resin again. Readjusting timer to check again in {resin_remaining_time}", color=3092790)
                            await channel.send(embed=embed)
                            new_time = current_time + unix_resin - 600
                            time_data = {"time": new_time}
                            database.child("boon").child("notes").child("reminders").child(reminder).update(time_data)
                except Exception as e:
                    embed = discord.Embed(title="Error: Resin Reminder", description="An error has occurred. TofuBoy has been notified.", color=3092790)
                    error = discord.Embed(title="Error: Resin Reminder", description=f"Error message:\n```{e}```", color=3092790)
                    await channel.send(embed)
                    tofu = self.bot.get_user(int(459655669889630209))
                    await tofu.send(embed=error)
                    
                        


        

    @resinReminderCheck.before_loop
    async def before_printer(self):
        print('Waiting resin loop')
        await self.bot.wait_until_ready()
        
async def setup(bot):
    await bot.add_cog(resinReminder(bot))