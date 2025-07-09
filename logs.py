import discord
from discord.ext import commands
import asyncio
import time
from datetime import timedelta
import datetime
import os
import asqlite
import random
from random import randint


class LogsCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()    
    async def on_member_join(self, member:discord.Member):
        channel = member.guild.get_channel(1382321640507052052)
        embed = discord.Embed(title="Welcome to the CatGang Server!",
                              description="- You are now officially a cat gangster! <a:error_cat:1339247313310191740>",
                              color=0xfff792,
                              timestamp=discord.utils.utcnow())
        embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.guild.icon.url)
        await channel.send(f"{member.mention}", embed=embed)
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        channel = member.guild.get_channel(1382321640507052052)
        embed = discord.Embed(title="You left the CatGang Server! Why?",
                              description="- Now you're not a cat ganster anymore :( <a:scream_cat:1339243936924962826>",
                              color=0xb82407,
                              timestamp=discord.utils.utcnow())
        embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.guild.icon.url)
        await channel.send(f"{member.mention}",embed=embed)


async def setup(bot:commands.Bot):
    await bot.add_cog(LogsCog(bot))