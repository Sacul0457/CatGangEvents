import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import time
from datetime import timedelta
import datetime
import os
import asqlite
import random
from random import randint


to_pick_from : list = ["cat", "none", "othing"]

def calc_guess(time_taken : float) -> int:
    earnings = 200 - (time_taken / 900) * 100
    return int(earnings)

class GuessView(discord.ui.View):
    def __init__(self, start_time : float, bot:commands.Bot):
        super().__init__(timeout=600)
        random_choice = tuple(random.sample(to_pick_from, 3))
        self.first, self.second, self.third = random_choice
        self.start_time = start_time
        self.bot = bot
        self.messsage :discord.Message | None = None


    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary, custom_id="button1")
    async def button1(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if self.first == "cat":
            time_taken = time.perf_counter() - self.start_time
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
            earned = calc_guess(time_taken)
            embed = discord.Embed(title=f"",
                                  description=f"- You have earned `🪙{earned}`!\n- You took: `{int(time.perf_counter() - self.start_time)}s`",
                                  color=discord.Color.brand_green(),
                                  timestamp=discord.utils.utcnow())
            embed.set_author(name=f"@{interaction.user} won!", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
            async with self.bot.economy_pool.acquire() as conn:
                row = await conn.execute('''SELECT money FROM economydb WHERE user_id = ?''',(interaction.user.id,))
                result = await row.fetchone()
                amount = result["money"] if result is not None else 0
                new_amount = amount + earned
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''',
                                   (interaction.user.id, new_amount))
                await conn.commit()
        else:
            embed = discord.Embed(title="Wrong one!",
                                  description="Try again, don't give up!",
                                  color=discord.Color.brand_red())
            
            await interaction.followup.send(embed=embed, ephemeral=True)
    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary, custom_id="button2")
    async def button2(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if self.second == "cat":
            time_taken = time.perf_counter() - self.start_time
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
            earned = calc_guess(time_taken)
            embed = discord.Embed(title=f"",
                                  description=f"- You have earned `🪙{earned}`!\n- You took: `{int(time.perf_counter() - self.start_time)}s`",
                                  color=discord.Color.brand_green(),
                                  timestamp=discord.utils.utcnow())
            embed.set_author(name=f"@{interaction.user} won!", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
            async with self.bot.economy_pool.acquire() as conn:
                row = await conn.execute('''SELECT money FROM economydb WHERE user_id = ?''',(interaction.user.id,))
                result = await row.fetchone()
                amount = result["money"] if result is not None else 0
                new_amount = amount + earned
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''',
                                   (interaction.user.id, new_amount))
                await conn.commit()
        else:
            embed = discord.Embed(title="Wrong one!",
                                  description="Try again, don't give up!",
                                  color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary, custom_id="button3")
    async def button3(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if self.third == "cat":
            time_taken = time.perf_counter() - self.start_time
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
            earned = calc_guess(time_taken)
            embed = discord.Embed(title="",
                                  description=f"- You have earned `🪙{earned}`!\n- You took: `{int(time.perf_counter() - self.start_time)}s`",
                                  color=discord.Color.brand_green(),
                                  timestamp=discord.utils.utcnow())
            embed.set_author(name=f"@{interaction.user} won!", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
            async with self.bot.economy_pool.acquire() as conn:
                row = await conn.execute('''SELECT money FROM economydb WHERE user_id = ?''',(interaction.user.id,))
                result = await row.fetchone()
                amount = result["money"] if result is not None else 0
                new_amount = amount + earned
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''',
                                   (interaction.user.id, new_amount))
                await conn.commit()
        else:
            embed = discord.Embed(title="Wrong one!",
                                  description="Try again, don't give up!",
                                  color=discord.Color.brand_red())
            
            await interaction.followup.send(embed=embed, ephemeral=True)


class EventCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.count1 = 0
        self.count2 = 0

    async def cog_load(self):
        self.task1.start()
        self.task2.start()

    def calculate_meow(self, time_seconds) -> int:
        time_seconds = max(0, min(300, time_seconds))
        score = 100 + ((300 - time_seconds) / 300) * 100
        return round(score)

    @tasks.loop(hours=1)
    async def task1(self) -> None:
        self.count1 += 1
        if self.count1 % 2 == 0:
            return
        channel = self.bot.get_channel(1319213192873775218) or await self.bot.fetch_channel(1319213192873775218)
        embed = discord.Embed(title="Minigames!",
                              description=f"- First one to type `meow` wins!\
                                \n- Starts in: <t:{int(time.time()) + 2}:R>",
                                color=0xff8a42)
        await channel.send(embed=embed)
        await asyncio.sleep(2.0)
        start_time = time.perf_counter()
        def check(msg :discord.Message):
            return msg.channel == channel and msg.content.lower() == "meow"
        try:
            message = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            await channel.send(f"The game has ended, sadly no one won :(")
            return
        else:
            time_taken = time.perf_counter() - start_time
            earned = self.calculate_meow(time_taken)
            embed = discord.Embed(title=f"",
                                description=f"- You earned `🪙{earned}`\n- You took: `{time_taken:.2f}s`",
                                timestamp=discord.utils.utcnow(),
                                color=discord.Color.brand_green())
            embed.set_author(name=f"@{message.author} won!", icon_url=message.author.display_avatar.url)
            await message.reply(embed=embed)
            async with self.bot.economy_pool.acquire() as conn:
                row = await conn.execute('''SELECT money FROM economydb WHERE user_id =?''',
                                         (message.author.id,))
                result = await row.fetchone()
                amount = result["money"] if result is not None else 0
                new_amount = amount + earned
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''',
                                   (message.author.id, new_amount))
        

    @tasks.loop(hours=1)
    async def task2(self) -> None:
        self.count2 += 1
        if self.count2 % 2 != 0:
            return
        channel = self.bot.get_channel(1319213192873775218) or await self.bot.fetch_channel(1319213192873775218)
        view = GuessView(time.perf_counter(), self.bot)
        embed = discord.Embed(title="Minigames!",
                              description=f"- Choose the right button to win!\
                                \n- Ends in: <t:{int(time.time()) + 600}:R>",
                              color=0xff8a42,)
        message = await channel.send(embed=embed,view=view)
        view.message = message #Assigns self.message to the message sent

async def setup(bot:commands.Bot):
    await bot.add_cog(EventCog(bot))