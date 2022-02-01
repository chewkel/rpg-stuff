from aiohttp import ClientSession
import discord
from discord.ext import commands
import random

class stuff(commands.Cog):
    def __init__(self,client):
        self.client = client



    @commands.command()
    async def ping(self,ctx):
        await ctx.send(f'Ping! Pong! You got a latency of {round(self.client.latency * 1000)} ms')
        
    @commands.command(aliases=['8ball', 'test'])
    async def _8ball(self,ctx, *, question):
        responses = [
            'It is certain.',
            'It is decidedly so.',
            'Without a doubt.',
            'Yes most definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            'Reply hazy, try again.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Concentrate and ask again.',
            "Don't count on it.",
            'My reply is a no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.',
            'I will respond later when im less busy with your mom.',
            "sure, I literally couldn't care less.",
            'Yes, idiot.',
            'Can you not?',
            'Yes, No, Maybe... I dont know, could you repeat the question?',
            'No... I mean yes... Well... Ask again later.',
        ]
        await ctx.send(
            f'```Question: {question}\nAnswer: {random.choice(responses)}```', allowed_mentions=discord.AllowedMentions(everyone=False,roles=False,users=False))
    
    @commands.command()
    async def say(self,ctx, *, content:str):
        await ctx.send(content)

    @commands.command(pass_context=True)
    async def hmm(self,ctx):
        if ctx.message.author.id == 212160821990522881:
            await ctx.send("hmm")

    @commands.command(aliases=['profilepic','pfp',"av"])
    async def avatar(self,ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        embed = discord.Embed(color=0x40cc88, timestamp=ctx.message.created_at)
        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(stuff(client))
