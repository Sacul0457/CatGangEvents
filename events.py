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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cats import EventBot

to_pick_from : tuple = ("cat", "no", "nope")

def calc_guess(time_taken : float) -> int:
    earnings = 200 - (time_taken / 900) * 100
    return int(earnings)

class GuessView(discord.ui.View):
    def __init__(self, start_time : float, bot: EventBot):
        super().__init__(timeout=600)
        random_choice = tuple(random.sample(to_pick_from, 3))
        self.first, self.second, self.third = random_choice
        self.start_time = start_time
        self.bot = bot
        self.messsage :discord.Message | None = None
        self.users :list[int] = []

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.messsage.edit(view=self)
        
    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary, custom_id="button1")
    async def button1(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id in self.users:
            return await interaction.followup.send(f"You can only try once! This is your second attempt :(", ephemeral=True)
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
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = money + excluded.money''',
                                   (interaction.user.id, earned))
                await conn.commit()
        else:
            embed = discord.Embed(title="Wrong one!",
                                  description="Sadly you can only try once",
                                  color=discord.Color.brand_red())
            self.users.append(interaction.user.id)
            await interaction.followup.send(embed=embed, ephemeral=True)
    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary, custom_id="button2")
    async def button2(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id in self.users:
            return await interaction.followup.send(f"You can only try once! This is your second attempt :(", ephemeral=True)
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
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = money + excluded.money''',
                                   (interaction.user.id, earned))
                await conn.commit()
        else:
            embed = discord.Embed(title="Wrong one!",
                                  description="Sadly you can only try once",
                                  color=discord.Color.brand_red())
            self.users.append(interaction.user.id)
            await interaction.followup.send(embed=embed, ephemeral=True)
    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary, custom_id="button3")
    async def button3(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id in self.users:
            return await interaction.followup.send(f"You can only try once! This is your second attempt :(", ephemeral=True)
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
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = money + excluded.money''',
                                   (interaction.user.id, earned))
                await conn.commit()
        else:
            try:
                embed = discord.Embed(title="Wrong one!",
                                      description="Sadly you can only try once",
                                      color=discord.Color.brand_red())
                self.users.append(interaction.user.id)
                await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception as e:
                print(e)

class RPCView(discord.ui.View):
    def __init__(self, bot : EventBot):
        super().__init__(timeout=600)
        self.add_item(RPCSelect(bot))
        self.message : discord.Message | None = None

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class RPCSelect(discord.ui.Select):
    def __init__(self, bot:EventBot):
        options = [discord.SelectOption(label="Rock", value="rock", emoji="🪨"),
                   discord.SelectOption(label="Paper", value="paper", emoji="📃"),
                   discord.SelectOption(label="Scissors", value="scissors", emoji="✂️")]
        super().__init__(custom_id="RPCSelect", placeholder="Choose Rock, Paper or Scissors... ", min_values=1, max_values=1, options=options)
        self.bot = bot
    
    def rps_winner(self, choice1: str, choice2: str) -> str:
        win_map = {
            "Rock": "Scissors",
            "Scissors": "Paper",
            "Paper": "Rock"
        }

        if choice1 == choice2:
            return  "Tie"
        elif win_map[choice1] == choice2:
            return "True"
        else:
            return "False"
        
    async def callback(self, interaction:discord.Interaction):
        value = self.values[0]
        async with self.bot.economy_pool.acquire() as conn:
            row = await conn.execute('''SELECT money FROM economydb WHERE user_id = ?''',(interaction.user.id,))
            result = await row.fetchone()
            if result is not None:
                amount = result["money"]
            else:
                amount = 0
            rand_ans = random.choice(["Rock", "Paper", "Scissors"])
            eraned_or_lose = randint(80, 150)
            if rand_ans != value:
                result = self.rps_winner(value, rand_ans)
                if result == "True":
                    total = amount + eraned_or_lose
                else:
                    total = max(amount - eraned_or_lose, 0)
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''', (interaction.user.id, total))
                await conn.commit()
        if result == "True":
            embed = discord.Embed(title=f"You won!",
                                description=f"- You earned 🪙**{eraned_or_lose} catbucks.** Well done!\
                                    \n- You chose: `{eraned_or_lose}` | The bot: `{rand_ans}`",
                                color=discord.Color.brand_green())
            embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        elif result == "False":
            embed = discord.Embed(title=f"You lost D:",
                                description=f"- You let 🪙**{eraned_or_lose} catbucks go down the drain...** \
                                    \n- You chose: `{eraned_or_lose}` | The bot: `{rand_ans}`",
                                color=discord.Color.brand_red())
            embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        else:
            embed = discord.Embed(title=f"It's a tie!",
                                description=f"- You chose: `{eraned_or_lose}` | The bot: `{rand_ans}`")
            embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)


class EventCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.count1 = 0
        self.count2 = 0

    async def cog_load(self):
        self.task1.start()
        self.task2.start()
    
    @tasks.loop(hours=1)
    async def task1(self) -> None:
        self.count1 += 1
        if self.count1 % 2 ==0:
            return
        channel = self.bot.get_channel(1319213192873775218) or await self.bot.fetch_channel(1319213192873775218)
        view= RPCView(self.bot)
        embed = discord.Embed(title="Minigames!",
                              description=f"- Play **Rock, Paper, Scissors**!\
                                \n- Ends in: <t:{int(time.time()) + 600}:R>",
                              color=0xff8a42,)
        message = await channel.send(embed=embed, view=view)
        view.message = message

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
        view.messsage = message #Assigns self.message to the message sent

async def setup(bot:commands.Bot):
    await bot.add_cog(EventCog(bot))
