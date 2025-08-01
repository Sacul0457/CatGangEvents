import discord
from discord import app_commands
from discord.ext import commands
import time
import os
import asyncio
from datetime import timedelta
import datetime
from dotenv import load_dotenv
load_dotenv()
import typing
import asqlite
import random
TOKEN = os.getenv("TOKEN")

cogs_list = ("logs", "events", "economy", "levels")


async def main():
    async with asqlite.connect("economy.db") as conn, asqlite.connect("level.db") as conn2:
        await conn.execute('''CREATE TABLE IF NOT EXISTS economydb(
            user_id INTEGER PRIMARY KEY,
            money INTEGER)''')
        await conn2.execute(''' CREATE TABLE IF NOT EXISTS leveldb(
                          user_id INTEGER PRIMARY KEY,
                          xp INTEGER)''')
        await conn.commit()
        await conn2.commit()
asyncio.run(main())

class EventBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.none()
        intents.guilds=True
        intents.members = True
        intents.message_content = True
        intents.guild_messages = True
        intents.moderation = True
        super().__init__(command_prefix=commands.when_mentioned, help_command=None, intents=intents, strip_after_prefix= True)
    async def setup_hook(self):
        for cog in cogs_list:
            try:
                await self.load_extension(cog)
                print(f"Loaded: {cog}!")
            except Exception as e:
                print(e)
        asyncio.get_event_loop().set_debug(True)
        self.economy_pool = await asqlite.create_pool("economy.db", size=4)
        self.level_pool = await asqlite.create_pool("level.db", size=3)


    async def close(self):
        await self.economy_pool.close()
        await self.level_pool.close()
        await super().close()


bot = EventBot()

@bot.event
async def on_command_error(ctx:commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(error)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandNotFound):
        return
    elif isinstance(error, commands.MemberNotFound):
        return await interaction.response.send_message(f"The member is no longer in the server or there is no such member.")
    elif isinstance(error, commands.UserNotFound):
        return await interaction.response.send_message(f"The user id in invalid.")
    elif isinstance(error, discord.app_commands.errors.TransformerError):
        await interaction.response.send_message(f"The member is no longer in the server.", ephemeral=True)
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        await interaction.response.send_message(f"I do not have the permission to use this command.", ephemeral=True)
    else:
        print(error)

@bot.command()
async def ping(ctx:commands.Context) -> None:
    if ctx.author.id != 802167689011134474:
        await ctx.send(f"Only the developer <@802167689011134474> can use this command!")
        return
    bot_latency = bot.latency * 1000
    embed = discord.Embed(title="Ping",
                          description=f"- Bot Latency: `{bot_latency:.2f}ms`")
    start_time = time.perf_counter()
    message = await ctx.send(embed=embed)
    end_time = time.perf_counter()
    api_latency = (end_time - start_time) * 1000
    embed.description = (f"- Bot Latency: `{bot_latency:.2f}ms`\n"
                         f"- API Latency: `{api_latency:.2f}ms`")
    await message.edit(embed=embed)

@bot.group(name="econs")
async def econs(ctx:commands.Context) -> None:
    if ctx.invoked_subcommand is None:
        await ctx.send(f"Missing subcommand!")
        return

@bot.command()
async def sync(ctx:commands.Context) -> None:
    if ctx.author.id != 802167689011134474:
        await ctx.send(f"Only the developer <@802167689011134474> can use this command!")
        return

    synced = await bot.tree.sync()
    await ctx.send(f"Successfully synced {len(synced)} commands.")

@econs.command()
async def fetch(ctx:commands.Context, user : discord.Member | discord.User) -> None:
    if ctx.author.id != 802167689011134474:
        await ctx.send(f"Only the developer <@802167689011134474> can use this command!")
        return
    async with bot.economy_pool.acquire() as conn:
        row = await conn.execute('''SELECT user_id, money FROM economydb where user_id = ?''', (user.id,))
        result = await row.fetchone()
    if result is not None:
        user_id = result["user_id"]
        amount = result["money"]
        await ctx.send(f"Success! `@{user.name}'s ({user.id})` ```- User ID: {user_id} \n- Money: {amount}```")
    else:
        await ctx.send(f"Unsuccessful fetch! ```No SQL found for {user.name} from economydb```")


@econs.command()
async def delete(ctx:commands.Context, user : discord.Member | discord.User) -> None:
    if ctx.author.id != 802167689011134474:
        await ctx.send(f"Only the developer <@802167689011134474> can use this command!")
        return
    async with bot.economy_pool.acquire() as conn:
        await conn.execute('''DELETE FROM economydb where user_id = ? ''', (user.id,))
        await conn.commit()
    await ctx.send(f"Success! Deleted: ```{user}'s ({user.id}) SQL row from economydb```")


@bot.group(name="levels")
async def levels(ctx:commands.Context) -> None:
    if ctx.invoked_subcommand is None:
        await ctx.send(f"Missing subcommand!")
        return

@levels.command()
async def fetch(ctx:commands.Context, user : discord.Member | discord.User) -> None:
    if ctx.author.id != 802167689011134474:
        await ctx.send(f"Only the developer <@802167689011134474> can use this command!")
        return
    async with bot.level_pool.acquire() as conn:
        row = await conn.execute('''SELECT user_id, xp FROM leveldb where user_id = ?''', (user.id,))
        result = await row.fetchone()
    if result is not None:
        user_id = result["user_id"]
        amount = result["xp"]
        await ctx.send(f"Success! `@{user.name}'s ({user.id})` ```- User ID: {user_id} \n- Xp: {amount}```")
    else:
        await ctx.send(f"Unsuccessful fetch! ```No SQL found for {user.name} in leveldb```")


@levels.command()
async def delete(ctx:commands.Context, user : discord.Member | discord.User) -> None:
    if ctx.author.id != 802167689011134474:
        await ctx.send(f"Only the developer <@802167689011134474> can use this command!")
        return
    async with bot.level_pool.acquire() as conn:
        await conn.execute('''DELETE FROM leveldb where user_id = ?''', (user.id,))
        await conn.commit()
    await ctx.send(f"Success! Deleted: ```{user}'s ({user.id}) SQL row from leveldb```")

bot.run(TOKEN)
