import discord
from discord.ext import commands, tasks
import time
from random import randint
import asqlite
import asyncio
import math
import typing
from discord import app_commands
import datetime

if typing.TYPE_CHECKING:
    from cats import EventBot

ADMIN_ROLES = (1343579448020308008, 1363492577067663430, 1319213465390284860,1373321679132033124, 1356640586123448501, 1343556153657004074, 1294291057437048843)
GUILD_ID = 1294290832219963563 #1319213192064536607
class AddModal(discord.ui.Modal):
    def __init__(self, bot:commands.Bot, cog: commands.Cog):
        super().__init__(title="Add Xp/Level", timeout=3600)
        self.user = discord.ui.TextInput(label="User", placeholder="Use a USER ID", required=True, style=discord.TextStyle.short)
        self.xp_or_level = discord.ui.TextInput(label="Xp or Level", placeholder="Just enter: 'xp' or 'level'", required=True, style=discord.TextStyle.short)
        self.amount = discord.ui.TextInput(label="Amount", placeholder="Amount to add, e.g: 10, 50, 300", style=discord.TextStyle.short, required="True")
        self.add_item(self.user)
        self.add_item(self.xp_or_level)
        self.add_item(self.amount)
        self.bot = bot
        self.cog = cog
    async def on_submit(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        user_id = self.user.value
        amount = self.amount.value
        xp_or_level = self.xp_or_level.value
        if not user_id.isdigit():
            embed = discord.Embed(title="Invalid User!",
                                description=f"The user ID `{user_id}` is invalid!",
                                color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            member = interaction.guild.get_member(int(user_id)) or interaction.guild.fetch_member(int(user_id))
        except discord.NotFound:
            embed = discord.Embed(title="Invalid User!",
                                description=f"The user ID `{user_id}` is invalid!",
                                color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not amount.isdigit():
            embed = discord.Embed(title="An error occurred!",
                                    description=f"`{amount}` is not a valid amount.",
                                    color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        current_xp = await self.cog.get_xp(member.id)
        if xp_or_level.lower() == "xp":
            total_xp = int(amount) + current_xp
            current_level = self.cog.get_level(total_xp)
        elif xp_or_level.lower() == "level":
            xp_from_level = self.cog.get_xp_from_level(int(amount))
            total_xp =  current_xp + xp_from_level
            current_level = self.cog.get_level(total_xp)
        else:
            embed = discord.Embed(title="An error occurred!",
                                    description=f"`{xp_or_level}` is invalid!\nChoose `xp` or `level` only.",
                                    color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return       
        embed = discord.Embed(title="Success!",
                                description=f"- Added: {amount} to {member.mention}\n- Total XP: `{total_xp}`\
                                \n- Current Level: {current_level}",
                                color=discord.Color.brand_green(),
                                timestamp=discord.utils.utcnow())
        embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)
        async with self.bot.level_pool.acquire() as conn:
            await conn.execute('''INSERT INTO leveldb (user_id, xp) VALUES (?, ?)
                                ON CONFLICT(user_id) DO UPDATE SET xp = excluded.xp''',
                                (member.id, total_xp))
class SetModal(discord.ui.Modal):
    def __init__(self, bot:commands.Bot, cog:commands.Cog):
        super().__init__(title="Set catbucks", timeout=3600)
        self.user = discord.ui.TextInput(label="User", placeholder="Use a USER ID", required=True, style=discord.TextStyle.short)
        self.xp_or_level = discord.ui.TextInput(label="Xp or Level", placeholder="Just enter: 'xp' or 'level'", required=True, style=discord.TextStyle.short)
        self.amount = discord.ui.TextInput(label="Amount", placeholder="Amount to set, e.g: 10, 50, 300", style=discord.TextStyle.short, required="True")
        self.add_item(self.user)
        self.add_item(self.xp_or_level)
        self.add_item(self.amount)
        self.bot = bot
        self.cog = cog
    async def on_submit(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        user_id = self.user.value
        amount = self.amount.value
        xp_or_level = self.xp_or_level.value
        if not user_id.isdigit():
            embed = discord.Embed(title="Invalid User!",
                                description=f"The user ID `{user_id}` is invalid!",
                                color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            member = interaction.guild.get_member(int(user_id)) or interaction.guild.fetch_member(int(user_id))
        except discord.NotFound:
            embed = discord.Embed(title="Invalid User!",
                                description=f"The user ID `{user_id}` is invalid!",
                                color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not amount.isdigit():
            embed = discord.Embed(title="An error occurred!",
                                    description=f"`{amount}` is not a valid amount.",
                                    color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if xp_or_level.lower() == "xp":
            current_level = self.cog.get_level(int(amount))
            new_xp = amount

        elif xp_or_level.lower() == "level":
            new_xp = self.cog.get_xp_from_level(int(amount))
            current_level = amount
        else:
            embed = discord.Embed(title="An error occurred!",
                                    description=f"`{xp_or_level}` is invalid!\nChoose `xp` or `level` only.",
                                    color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return         

        embed = discord.Embed(title="Success!",
                                description=f"- Set: {new_xp} to {member.mention}\
                                \n- Current Level: {current_level}",
                                color=discord.Color.brand_green(),
                                timestamp=discord.utils.utcnow())
        embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)
        async with self.bot.level_pool.acquire() as conn:
            await conn.execute('''INSERT INTO leveldb (user_id, xp) VALUES (?, ?)
                                ON CONFLICT(user_id) DO UPDATE SET xp = excluded.xp''',
                                (member.id, new_xp))
    
class RemoveModal(discord.ui.Modal):
    def __init__(self, bot:commands.Bot, cog:commands.Cog):
        super().__init__(title="Remove Catbucks", timeout=3600)
        self.user = discord.ui.TextInput(label="User", placeholder="Use a USER ID", required=True, style=discord.TextStyle.short)
        self.xp_or_level = discord.ui.TextInput(label="Xp or Level", placeholder="Just enter: 'xp' or 'level'", required=True, style=discord.TextStyle.short)
        self.amount = discord.ui.TextInput(label="Amount", placeholder="Amount to remove, e.g: 10, 50, 300", style=discord.TextStyle.short, required="True")
        self.add_item(self.user)
        self.add_item(self.xp_or_level)
        self.add_item(self.amount)
        self.bot = bot
        self.cog = cog
    async def on_submit(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        user_id = self.user.value
        amount = self.amount.value
        xp_or_level = self.xp_or_level.value
        if not user_id.isdigit():
            embed = discord.Embed(title="Invalid User!",
                                description=f"The user ID `{user_id}` is invalid!",
                                color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            member = interaction.guild.get_member(int(user_id)) or interaction.guild.fetch_member(int(user_id))
        except discord.NotFound:
            embed = discord.Embed(title="Invalid User!",
                                description=f"The user ID `{user_id}` is invalid!",
                                color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not amount.isdigit():
            embed = discord.Embed(title="An error occurred!",
                                    description=f"`{amount}` is not a valid amount.",
                                    color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        current_xp = await self.cog.get_xp(member.id)
        if xp_or_level.lower() == "xp":
            total_xp = current_xp - int(amount)
            current_level = self.cog.get_level(total_xp)
        elif xp_or_level.lower() == "level":
            xp_from_level = self.cog.get_xp_from_level(int(amount))
            total_xp = current_xp - xp_from_level
            current_level = self.cog.get_level(total_xp)
        else:
            embed = discord.Embed(title="An error occurred!",
                                description=f"`{xp_or_level}` is invalid!\nChoose `xp` or `level` only.",
                                color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if total_xp < 0:
            embed = discord.Embed(title="An error occurred!",
                                    description=f"You cannot remove a member's level till less than 0!",
                                    color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
            return    
        embed = discord.Embed(title="Success!",
                            description=f"- Removed: {amount} from {member.mention}\n- Total XP: `{total_xp}`\
                                \n- Current Level: {current_level}",
                            color=discord.Color.brand_green(),
                            timestamp=discord.utils.utcnow())
        embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)
        async with self.bot.level_pool.acquire() as conn:
            await conn.execute('''INSERT INTO leveldb (user_id, xp) VALUES (?, ?)
                                ON CONFLICT(user_id) DO UPDATE SET xp = excluded.xp''',
                                (member.id, total_xp))


class AdminView(discord.ui.View):
    def __init__(self, bot:EventBot, cog:commands.Cog):
        super().__init__(timeout=3600)
        self.bot = bot
        self.cog = cog
    @discord.ui.button(label="Add", emoji="➕", style=discord.ButtonStyle.green, custom_id="addbutton")
    async def button1(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(AddModal(self.bot, self.cog))
    @discord.ui.button(label="Remove", emoji="➖", style=discord.ButtonStyle.red, custom_id="removebutton")
    async def button2(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(RemoveModal(self.bot, self.cog))
    @discord.ui.button(label="Set", emoji="🟰", style=discord.ButtonStyle.secondary, custom_id="setbutton")
    async def button3(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(SetModal(self.bot, self.cog))  

class LevelCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.user_xp = {}
        self.xp_lock = asyncio.Lock()
    async def cog_load(self):
        self.save_data.start()
        self.weekly_reward.start()

    async def get_xp(self, user_id : int) -> int:
        async with self.bot.level_pool.acquire() as conn:
            row = await conn.execute('''SELECT xp FROM leveldb WHERE user_id = ? ''', (user_id,))
            result = await row.fetchone()
        if result is not None:
            xp = result["xp"]
            return xp
        return 0
        
    def get_level(self, xp:int) -> int:
        return xp // 350


    def check_level_up(self, old_xp: int, new_xp: int) -> int | None: 
        old_level =  self.get_level(old_xp)
        new_level = self.get_level(new_xp) #
        if new_level > old_level:
            return new_level
        return None
    def get_xp_from_level(self, level: int) -> int: 
         return 350 * level
    
    async def check_role(self, pending_roles : dict) -> None:
        guild = self.bot.get_guild(1319213192064536607)
        for user_id, new_xp in pending_roles.items():
            member = guild.get_member(int(user_id))
            if member is None:
                continue
            if new_xp >= 70000: #200
                role_id = 1346229335052386385
            elif new_xp >= 35000: #100
                role_id = 1333829412939890781
            elif new_xp >= 17500: #50
                role_id = 1333829256869969940
            elif new_xp >= 10500: #30
                role_id = 1384914063817048076
                await member.remove_roles(discord.Object(1384913772027711498))
            elif new_xp >= 7000: #20
                role_id = 1384913772027711498
                await member.remove_roles(discord.Object(1333828407070429257))
            else:
                role_id = 1333828407070429257
            await member.add_roles(discord.Object(role_id))
    @tasks.loop(seconds=30)
    async def save_data(self):
        if not self.user_xp:
            return

        to_level_up = {}
        pending_roles = {}
        update_data = []
        query_value = ",".join("?" for _ in range(len(self.user_xp.keys())))
        async with self.bot.level_pool.acquire() as conn, self.xp_lock:
            async with conn.transaction():
                rows = await conn.execute(f'''SELECT user_id, xp FROM leveldb where user_id IN ({query_value})''', tuple(self.user_xp.keys()))
                results = await rows.fetchall()
                xp_map = {row["user_id"] : row["xp"] for row in results}

                for user_id, xp in self.user_xp.items():
                    current_xp = xp_map.get(user_id, 0) 
                    new_xp = xp + current_xp
                    update_data.append((user_id, new_xp))

                    level_up = self.check_level_up(current_xp, new_xp)
                    if level_up:
                        to_level_up[user_id] = level_up
                        if new_xp >= 3500:
                            pending_roles[user_id] = new_xp
                await conn.executemany('''INSERT INTO leveldb (user_id, xp) VALUES (?, ?)
                                    ON CONFLICT(user_id) DO UPDATE SET xp = excluded.xp''',
                                    update_data)
            self.user_xp.clear()
            await conn.commit()

        if to_level_up:
            await self.process_level_ups(to_level_up, pending_roles)

    async def process_level_ups(self, to_level_up, pending_roles) -> None:
        channel = self.bot.get_channel(1350597714840260709)
        for user_id, level_up in to_level_up.items():
            await channel.send(f"<@{user_id}> You are now **level {level_up}!**")
        if pending_roles:
            await self.check_role(pending_roles)

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message) -> None:
        if message.author == self.bot.user or message.content.startswith(("<@1377619750460461076>", "<@1377185541816188928>")) or message.author.bot or message.channel.id != 1319213192873775218: 
            return
        user_id = message.author.id
        rich_cat_role = message.guild.get_role(1330928286200496180)
        async with self.xp_lock:
            self.user_xp[user_id] = self.user_xp.get(user_id, 0) + 10 if rich_cat_role not in message.author.roles else self.user_xp.get(user_id, 0) + 15
                
    @app_commands.command(name="level", description="Get the level of yourself or of another user")
    @app_commands.describe(member = "The member to get the level of")
    async def level(self, interaction:discord.Interaction, member: discord.Member | discord.User | None = None) -> None:
        await interaction.response.defer(thinking=True)
        member = member or interaction.user
        xp = await self.get_xp(member.id)
        level = self.get_level(xp)
        next_xp = self.get_xp_from_level(level+1)
        colour = member.top_role.color
        embed = discord.Embed(title="",
                              description=f"- **Level:** {level}\n- **Xp:** `{xp}/{next_xp}`",
                                color=colour,
                                timestamp=discord.utils.utcnow())
        embed.set_author(name=f"@{member.name}", icon_url=member.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="levels-admin", description="Get Admin commands for levels")
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def levelsadmin(self, interaction:discord.Interaction) -> None:
        embed = discord.Embed(title="Admin Commands for Levels",
                              color=discord.Color.blurple())
        embed.add_field(name="Add", value="- You cannot add a negative number.")
        embed.add_field(name="Remove", value="- You cannnot remove a member's xp/level till it's less than 0.", inline=False)
        embed.add_field(name="Set", value="- You cannot set a member's xp/level to less than 0.", inline=False)

        await interaction.response.send_message(embed=embed, view=AdminView(self.bot, self), ephemeral=True)
    
    @levelsadmin.error
    async def levelsadmin_error(self, interaction:discord.Interaction, error:app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.errors.MissingAnyRole):
            embed = discord.Embed(title="Missing Permissions!",
                                  description="You do not have the role/permission to use this command.",
                                  color=discord.Color.brand_red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            print(error)

    @app_commands.command(name="levels-leaderboard", description="Get the leaderboard for levels")
    async def levelsleaderboard(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        async with self.bot.level_pool.acquire() as conn:
            rows = await conn.execute('''SELECT * FROM leveldb ORDER BY xp DESC LIMIT 10 ''')
            results = await rows.fetchall()
        results_list = [f"<@{result['user_id']}> - Level {int(result['xp']// 350)} | `{result['xp']}`xp" for result in results]
        resuls_final = "\n- ".join(results_list)
        embed = discord.Embed(title="Level Leaderboard",
                              description=f"1. {resuls_final}",
                              color=discord.Color.blurple())
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.followup.send(embed=embed)
    
    @tasks.loop(time=datetime.time(hour=0))
    async def weekly_reward(self):
        now = datetime.datetime.now()
        if now.weekday() == 5:
            async with self.bot.level_pool.acquire() as conn:
                rows = await conn.execute('''SELECT user_id FROM leveldb ORDER BY xp DESC LIMIT 5 ''')
                results = await rows.fetchall()
            guild = self.bot.get_guild(GUILD_ID)
            for result in results:
                user_id = result["user_id"]
                try:
                    member = guild.get_member(user_id)
                except discord.NotFound:
                    continue
                await member.add_roles(discord.Object(1395723836351189093))


async def setup(bot:commands.Bot):
    await bot.add_cog(LevelCog(bot))
