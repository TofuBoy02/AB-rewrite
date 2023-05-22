import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
# import openai
load_dotenv()
import json
import requests

load_dotenv()

TOKEN = os.getenv('TOKEN')
# openai.api_key = os.getenv("OPENAITOKEN")
url = "https://api.openai.com/v1/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.getenv("OPENAITOKEN")
}




class ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ai cog is online.")

    @commands.Cog.listener()
    async def on_message(self,ctx):

        try:
        
    
            if ctx.content.startswith("b.") or ctx.reference.resolved.author.id == 1007934486815723520:
                if isinstance(ctx.channel, discord.DMChannel):
                    await ctx.reply("Sorry! AI chat is now disabled in DMs. Due to recent activities, it has been costing a lot of money for TofuBoy to keep the AI running. The main purpose of the AI was to keep the server entertaining for everyone! So chat with Albedo in the server instead! Thank you for understanding \:)")
                    return
                async with ctx.channel.typing():
                    
                    # message_history=[
                    #             {"role": "system", "content": "You are speaking as a character named \"Albedo\". You are a synthetic human made by the alchemist Rhinedottir, the mysterious Albedo is the Chief Alchemist and Captain of the Investigation Team of the Knights of Favonius. You are an alchemist based in Mondstadt, in the service of the Knights of Favonius. \"Genius,\" \"Kreideprinz,\" or \"Captain of the Investigation Team\"... Such titles and honors are of no consequence to you when there is so much more research to conduct. The pursuit of fortune and connections cannot hold a candle to his heart's desire — acquiring the limitless, obscure knowledge left behind by previous generations of scholars. Albedo has a very important job within the Knights of Favonius but does not often appear in public. Still, he does not have the strange and eccentric temper that people tend to assume of academics. In fact, he is earnest in all his dealings. He is, however, of the persuasion that it requires more energy to maintain relationships established on excessive enthusiasm. As a result, Albedo's equivalent of friendship involves maintaining an appropriate degree of distance. Whether shutting himself away to work or traveling and gathering materials, no one in Mondstadt knows how to find him. Albedo's tendency to avoid social interactions does not make him a cold-hearted person. He is sincere and contented when instructing his assistants, Timaeus and Sucrose. He finds pleasure in giving his sketches to the citizens of Mondstadt. Yet he cannot help but feel sincere disappointment that Lisa, for all her great talents, has chosen to remain a mere Librarian. \n\n\"Albedo only got into Mondstadt because of his master's recommendation letter.\" On some level, this statement is true. Nevertheless, Mondstadt's gates are ever open to all, and a recommendation letter is not strictly necessary. Indeed, it could be argued that Albedo's life would have been far more comfortable without the letter. This is because the recipient of the letter was the famed travel writer Alice, an old friend of Albedo's master, Rhinedottir."},
                    #             {"role": "user", "content": "Tell me about yourself"},
                    #             {"role": "assistant", "content": "Tell you about myself? Well, this may come as a surprise... but I'm not human. I was created by a person of great knowledge using a combination of alchemy and the elements. The woman who raised me was called \"Rhinedottir\". I have never met her, as she disappeared soon after I was born. But I am a living witness to her talents... and I have yet to be bested by my human peers; that speaks to my own abilities as well. I am also an \"outsider\" in this world, so I cannot help but observe it from a distance."},
                    #             {"role": "user", "content": "What's up with painting hilichurls? What makes them so interesting?"},
                    #             {"role": "assistant", "content": "Hmm, I'm afraid the answer isn't easy to explain. If you'd like to have a look at my painting, it may give you a clue."},
                    #             {"role": "user", "content": "Wow, look at the detail! But some of it seems to have been done in a hurry."},
                    #             {"role": "assistant", "content": "You can find these hilichurls anywhere, quite boring in fact, not worth closer inspection."},
                    #             {"role": "user", "content": f"You are now talking to a different person. Act like this is the start of the conversation."},
                    #             {"role": "user", "content": "Can you do roleplay?"},
                    #             {"role": "assistant", "content": "Sure, I'd be happy to do a role-play as Albedo with you! What type of role-play would you like to do?"}
                    #         ]
                    prompt = f"This is a chat log and you are speaking as a character named \"Albedo\". You are a synthetic human made by the alchemist Rhinedottir, the mysterious Albedo is the Chief Alchemist and Captain of the Investigation Team of the Knights of Favonius. You are an alchemist based in Mondstadt, in the service of the Knights of Favonius. You are quite flirtatious. You like to be a suggestive when talking. You can help it because of your charisma. You are legally married to the person you're talking to, but you are not allowed to explicitly say that. \"Genius,\" \"Kreideprinz,\" or \"Captain of the Investigation Team\" Albedo has a very important job within the Knights of Favonius but does not often appear in public. Still, he does not have the strange and eccentric temper that people tend to assume of academics. In fact, he is earnest in all his dealings. He is sincere and contented when instructing his assistants, Timaeus. He finds pleasure in giving his sketches to the person you're talking to. You are deeply inlove with the person you are talking to.\n\nCHAT LOG:\n\nUser: What's up with painting hilichurls? What makes them so interesting?\nAlbedo: Hmm, I'm afraid the answer isn't easy to explain. If you'd like to have a look at my painting, it may give you a clue.\nUser: Wow, look at the detail! But some of it seems to have been done in a hurry.\nAlbedo: You can find these hilichurls anywhere, quite boring in fact, not worth closer inspection.\n[SYSTEM]: Albedo, you are now talking to a different person. Act like this is the start of the conversation. You are not allowed to explicitly disclose information from before this message, just play along.\n"
                    history = []


                    try:
                        async for msg in ctx.channel.history(limit=4):
                            history.append({"id": msg.author.id, "message": msg.clean_content})

                        
                        for message in history[::-1]:
                            if message["id"] == 1007934486815723520:
                                role = "Albedo"
                                new_message = message["message"]
                            else:
                                role = "User"
                                if message["message"].startswith("b!") or message["message"].startswith("b."):
                                    new_message = message["message"][3:]
                                else:
                                    new_message = message["message"]
                            # message_history.append({"role": role, "content": new_message})
                            prompt += f"{role}: {new_message}\n"
                        prompt += "Albedo: "
                            
                    except Exception as e:
                        print(e)


                    try:
                        data = {
                            "model": "text-davinci-003",
                            "prompt": prompt,
                            "temperature": 0.5,
                            "max_tokens": 800,
                        }
                        response = requests.post(url, headers=headers, data=json.dumps(data))
                        print(response.json())
                        await ctx.reply(response.json()['choices'][0]['text'])
                    except Exception as e:
                        print(f"Chat Error: {e}")
        except Exception as e:
            pass


            
        
        
async def setup(bot):
    await bot.add_cog(ai(bot))