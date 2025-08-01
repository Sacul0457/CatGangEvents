import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time
from datetime import timedelta
import datetime
import os
import asqlite
import random
from random import randint
import typing
ADMIN_ROLES = (1343579448020308008, 1363492577067663430, 1319213465390284860,1373321679132033124, 1356640586123448501, 1343556153657004074, 1294291057437048843)

class ShopSelectMenu(discord.ui.Select):
    def __init__(self, bot:commands.Bot):
        options = [discord.SelectOption(label="VIP", description="🪙50000", value="vip"),
                   discord.SelectOption(label="King Cat", description="🪙25000", value="king"),
                   discord.SelectOption(label="Genius Cat", description="🪙12500", value="genius"),
                   discord.SelectOption(label="Rich Cat", description="🪙8000", value="rich"),
                   discord.SelectOption(label="Beluga", description="🪙5000", value="beluga"),
                   discord.SelectOption(label="Cat", description="🪙2500", value="cat")]
        super().__init__(placeholder="Click here to buy some roles!", min_values=1, max_values=1, options=options)
        self.bot= bot
    async def callback(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        async with self.bot.economy_pool.acquire() as conn:
            row = await conn.execute('''SELECT money FROM economydb where user_id = ?''',
                                     (interaction.user.id,))
            result = await row.fetchone()
        if result is not None:
            amount = result["money"]
        else:
            amount = 0
            embed = discord.Embed(title="Not enough money!",
                                  description="You currently have 🪙0!",
                                  color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed)
            return
        value = self.values[0]
        need = None
        if value == "vip":
            if amount >= 50000:
                cost =50000
                role = interaction.guild.get_role(1319214818527412337)
            else:
                need = 50000 - amount
        elif value == "king":
            if amount >= 25000:
                cost = 25000
                role = interaction.guild.get_role(1330927524816883783)
            else:
                need = 25000 - amount
        elif value == "genius":
            if amount >= 12500:
                cost =12500
                role = interaction.guild.get_role(1330927375340404807)
            else:
                need = 12500 - amount
        elif value == "rich":
            if amount >= 8000:
                cost =8000
                role = interaction.guild.get_role(1330928286200496180)
            else:
                need = 8000 - amount
        elif value == "beluga":
            if amount >= 5000:
                cost =5000
                role = interaction.guild.get_role(1333033719992422410)
            else:
                need = 5000 - amount
        else:
            if amount >= 2500:
                cost = 2500
                role = interaction.guild.get_role(1376000726077018112)
            else:
                need = 2500 - amount
        update_db = False
        if need is None:
            if role not in interaction.user.roles:
                embed = discord.Embed(title="Role Bought!",
                                      description=f"You now have the {role.mention} role! | 🪙{amount-cost} left",
                                      color=discord.Color.brand_green(), timestamp=discord.utils.utcnow())
                update_db = True
                ephemeral = False
                await interaction.user.add_roles(role)
            else:
                embed = discord.Embed(title="Error Occurred!",
                                      description=f"You already have the {role.mention} role!",
                                      color=discord.Color.brand_red())
                ephemeral = True

        else:
            embed = discord.Embed(title="Not enough catbucks!",
                                  description=f"You have `🪙{amount}`, you need `🪙{need}` more catbucks!",
                                  color=discord.Color.brand_red())
            ephemeral = True
        await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        if update_db == True:
            async with self.bot.economy_pool.acquire() as conn:
                await conn.execute('''UPDATE economydb SET money = ? WHERE user_id = ?''', (amount-cost, interaction.user.id))
                await conn.commit()
            
class ShopView(discord.ui.View): 
    def __init__(self, bot:commands.Bot):
        super().__init__(timeout=None)
        self.add_item(ShopSelectMenu(bot))


    
class AddModal(discord.ui.Modal):
    def __init__(self, bot:commands.Bot):
        super().__init__(title="Add Catbucks", timeout=3600)
        self.user = discord.ui.TextInput(label="User", placeholder="Use a USER ID", required=True, style=discord.TextStyle.short)
        self.amount = discord.ui.TextInput(label="Amount", placeholder="Amount to add, e.g: 300, 5000, 20000", style=discord.TextStyle.short, required="True")
        self.add_item(self.user)
        self.add_item(self.amount)
        self.bot = bot
    async def on_submit(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        user_id = self.user.value
        amount = self.amount.value
        member = None
        if user_id.isdigit():
            try:
                member = interaction.guild.get_member(int(user_id)) or interaction.guild.fetch_member(int(user_id))
            except discord.NotFound:
                pass
        if member is None:
            embed = discord.Embed(title="Invalid User!",
                                  description=f"The user ID `{user_id}` is invalid!",
                                  color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            if not amount.isdigit():
                embed = discord.Embed(title="An error occurred!",
                                      description=f"`{amount}` is not a valid amount.",
                                      color=discord.Color.brand_red())
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            async with self.bot.economy_pool.acquire() as conn:
                row = await conn.execute('''SELECT money FROM economydb where user_id = ? ''', (member.id))
                result = await row.fetchone()
            if result is None:
                old_amount = 0
            else:
                old_amount = result["money"]
            embed = discord.Embed(title="Success!",
                                  description=f"- Added: `🪙{amount}` to {member.mention}\n- Total: `🪙{int(amount) + old_amount}`",
                                  color=discord.Color.brand_green(),
                                  timestamp=discord.utils.utcnow())
            embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            async with self.bot.economy_pool.acquire() as conn:
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = money + excluded.money''', (member.id, int(amount)))
                await conn.commit()
    
class SetModal(discord.ui.Modal):
    def __init__(self, bot:commands.Bot):
        super().__init__(title="Set catbucks", timeout=3600)
        self.user = discord.ui.TextInput(label="User", placeholder="Use a USER ID", required=True, style=discord.TextStyle.short)
        self.amount = discord.ui.TextInput(label="Amount", placeholder="Amount to remove, e.g: 300, 5000, 20000", style=discord.TextStyle.short, required="True")
        self.add_item(self.user)
        self.add_item(self.amount)
        self.bot = bot
    async def on_submit(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        user_id = self.user.value
        amount = self.amount.value
        member = None
        if user_id.isdigit():
            try:
                member = interaction.guild.get_member(int(user_id)) or interaction.guild.fetch_member(int(user_id))
            except discord.NotFound:
                pass
        if member is None:
            embed = discord.Embed(title="Invalid User!",
                                  description=f"The user ID `{user_id}` is invalid!",
                                  color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            if not amount.isdigit():
                embed = discord.Embed(title="An error occurred!",
                                      description=f"`{amount}` is not a valid amount.",
                                      color=discord.Color.brand_red())
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            embed = discord.Embed(title="Success!",
                                description=f"- Set: `🪙{amount}` to {member.mention}",
                                color=discord.Color.brand_green(),
                                timestamp=discord.utils.utcnow())
            embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            async with self.bot.economy_pool.acquire() as conn:
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                   ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''', (member.id, int(amount)))
                await conn.commit()

    
class RemoveModal(discord.ui.Modal):
    def __init__(self, bot:commands.Bot):
        super().__init__(title="Remove Catbucks", timeout=3600)
        self.user = discord.ui.TextInput(label="User", placeholder="Use a USER ID", required=True, style=discord.TextStyle.short)
        self.amount = discord.ui.TextInput(label="Amount", placeholder="Amount to remove, e.g: 300, 5000, 20000", style=discord.TextStyle.short, required="True")
        self.add_item(self.user)
        self.add_item(self.amount)
        self.bot = bot
    async def on_submit(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        user_id = self.user.value
        amount = self.amount.value
        member = None
        if user_id.isdigit():
            try:
                member = interaction.guild.get_member(int(user_id)) or interaction.guild.fetch_member(int(user_id))
            except discord.NotFound:
                pass
        if member is None:
            embed = discord.Embed(title="Invalid User!",
                                  description=f"The user ID `{user_id}` is invalid!",
                                  color=discord.Color.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            if not amount.isdigit():
                embed = discord.Embed(title="An error occurred!",
                                      description=f"`{amount}` is not a valid amount.",
                                      color=discord.Color.brand_red())
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            async with self.bot.economy_pool.acquire() as conn:
                row = await conn.execute('''SELECT money FROM economydb where user_id = ? ''', (member.id))
                result = await row.fetchone()
            if result is None:
                old_amount = 0
            else:
                old_amount = result["money"]
            if (old_amount - int(amount)) < 0:
                embed = discord.Embed(title="Error Occurred!",
                                      description="You cannot remove a member's catbucks to a negative amount.",
                                      color=discord.Color.brand_green())
                embed.add_field(name="Details", value=f">>> - Amount to Remove: 🪙{amount}\n- Current Amount: `🪙{old_amount}`")
                embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title="Success!",
                                    description=f"- Removed: `🪙{amount}` from {member.mention}\n- Total: `🪙{old_amount - int(amount)}`",
                                    color=discord.Color.brand_green(),
                                    timestamp=discord.utils.utcnow())
                embed.set_author(name=f"@{member}", icon_url=member.display_avatar.url)
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                async with self.bot.economy_pool.acquire() as conn:
                    await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                    ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''', (member.id, old_amount-int(amount)))
                    await conn.commit()


class AdminView(discord.ui.View):
    def __init__(self, bot:commands.Bot):
        super().__init__(timeout=3600)
        self.bot = bot
    @discord.ui.button(label="Add", emoji="➕", style=discord.ButtonStyle.green, custom_id="addbutton")
    async def button1(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(AddModal(self.bot))
    @discord.ui.button(label="Remove", emoji="➖", style=discord.ButtonStyle.red, custom_id="removebutton")
    async def button2(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(RemoveModal(self.bot))
    @discord.ui.button(label="Set", emoji="🟰", style=discord.ButtonStyle.secondary, custom_id="setbutton")
    async def button3(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(SetModal(self.bot))    


class EconomyCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name="work", description="Do work, get paid!")
    @app_commands.checks.cooldown(1, 180)
    async def work(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        earned = randint(50, 100)
        vip = interaction.guild.get_role(1319214818527412337)
        booster = interaction.guild.get_role(1338543708659777599)
        if any(role in interaction.user.roles for role in (vip, booster)):
            extra = randint(10,30)
        else:
            extra = 0
        async with self.bot.economy_pool.acquire() as conn:
            await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                               ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''', (interaction.user.id, (extra + earned)))
            await conn.commit()
        embed = discord.Embed(title=f"Work - {interaction.user.name}",
                              description=f"You earned 🪙**{earned} catbucks.** Well done!",
                              color=discord.Color.blue())
        embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        if extra != 0:
            embed.add_field(name="", value=f"-# Since you are a VIP/Booster, you are given an extra 🪙**{extra} catbucks!**")
        await interaction.followup.send(embed=embed)

    @work.error
    async def work_error(self, interaction:discord.Interaction, error:app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed =discord.Embed(title="Cooldown!",
                                 description=f"Try again <t:{int(time.time()) + int(error.retry_after)}:R>!",
                                 color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            print(error)

    @app_commands.command(name="coinflip", description="Choose heads or tails")
    @app_commands.describe(bet="How much you want to bet (80-150)", choice="Heads or Tails")
    @app_commands.checks.cooldown(1, 300)
    async def coinflip(self, interaction:discord.Interaction, bet:app_commands.Range[int, 80, 150], choice:typing.Literal["Heads", "Tails"]) -> None:
        await interaction.response.defer(thinking=True)
        async with self.bot.economy_pool.acquire() as conn:
            row = await conn.execute('''SELECT money FROM economydb WHERE user_id = ?''',(interaction.user.id,))
            result = await row.fetchone()
            if result is not None:
                amount = result["money"]
            else:
                amount = 0
            rand_ans = random.choice(["Heads", "Tails"])
            if rand_ans == choice:
                total = amount + bet
            else:
                total = max(amount - bet, 0)
            await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                            ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''', (interaction.user.id, total))
            await conn.commit()
        if rand_ans == choice:
            embed = discord.Embed(title=f"{rand_ans}! | You won!",
                                description=f"You earned 🪙**{bet} catbucks.** Well done!",
                                color=discord.Color.brand_green())
            embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        else:
            embed = discord.Embed(title=f"{rand_ans}... | You lost :(",
                                description=f"You lost 🪙**{bet} catbucks.**",
                                color=discord.Color.brand_red())
            embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @coinflip.error
    async def coinflip_error(self, interaction:discord.Interaction, error:app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed =discord.Embed(title="Cooldown!",
                                 description=f"Try again <t:{int(time.time()) + int(error.retry_after)}:R>!",
                                 color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            print(error)

    @app_commands.command(name="joke", description="Tell a joke hoping you earn money")
    @app_commands.checks.cooldown(1, 300)
    async def joke(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        async with self.bot.economy_pool.acquire() as conn:
            row = await conn.execute('''SELECT money FROM economydb WHERE user_id = ?''',(interaction.user.id,))
            result = await row.fetchone()
            if result is not None:
                amount = result["money"]
            else:
                amount = 0
            rand_ans = random.choice(["Not Funny", "Funny"])
            rand_amount = randint(50, 150)
            if rand_ans == "Funny":
                total = amount + rand_amount
            else:
                total = max(amount - rand_amount, 0)
            await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                            ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''', (interaction.user.id, total))
            await conn.commit()
        if rand_ans == "Funny":
            embed = discord.Embed(title=f"Your joke was hilarious LMAO!",
                                description=f"You earned 🪙**{rand_amount} catbucks.** What a comedian!",
                                color=discord.Color.brand_green())
            embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        else:
            embed = discord.Embed(title=f"Your joke was so bad...",
                                description=f"You lost 🪙**{rand_amount} catbucks.**",
                                color=discord.Color.brand_red())
            embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @joke.error
    async def joke_error(self, interaction:discord.Interaction, error:app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed =discord.Embed(title="Cooldown!",
                                 description=f"Try again <t:{int(time.time()) + int(error.retry_after)}:R>!",
                                 color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            print(error)

    @app_commands.command(name="balance", description="Check how much money you have!")
    @app_commands.describe(member="The member you want to check the balance of")
    async def balance(self, interaction:discord.Interaction, member:discord.Member | None = None) -> None:
        await interaction.response.defer(thinking=True)
        if member is not None:
            user = member
        else:
            user = interaction.user
        async with self.bot.economy_pool.acquire() as conn:
            row = await conn.execute('''SELECT money FROM economydb WHERE user_id = ?''',(user.id,))
            result = await row.fetchone()
        if result is not None:
            amount = result["money"]
        else:
            amount = 0

        embed = discord.Embed(title="Economy Stats",
                              description=f"You have 🪙**{amount} catbucks!**",
                              color=discord.Color.dark_gray())
        embed.set_author(name=f"@{user}", icon_url=user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="shop", description="See the list of things you can buy with catbucks!")
    async def shop(self, interaction:discord.Interaction) -> None:
        embed = discord.Embed(title=f"Shop!",
                                color=discord.Color.blurple())
        embed.add_field(name="", value="1. <@&1319214818527412337> \n  - 🪙50000 \n\n4. <@&1330928286200496180> \n  - 🪙8000")
        embed.add_field(name="", value="2. <@&1330927524816883783> \n  - 🪙25000\n\n5. <@&1333033719992422410> \n  - 🪙5000")
        embed.add_field(name="", value="3. <@&1330927375340404807> \n  - 🪙12500\n\n6. <@&1376000726077018112> \n  - 🪙2500")
        embed.set_thumbnail(url=interaction.guild.icon.url)

        await interaction.response.send_message(embed=embed, view=ShopView(self.bot))

    @app_commands.command(name="econs-admin", description="Use Economy Admin Commands")
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def econsadmin(self, interaction:discord.Interaction) -> None:
        embed = discord.Embed(title="Admin Commands",
                              color=discord.Color.blurple(),
                              timestamp=discord.utils.utcnow())
        embed.add_field(name="Add", value="- You cannot add a negative number.")
        embed.add_field(name="Remove", value="- You cannnot remove a member's catbuck till it's less than 0.", inline=False)
        embed.add_field(name="Set", value="- You cannot set a member's catbucks to less than 0.", inline=False)

        await interaction.response.send_message(embed=embed, view=AdminView(self.bot), ephemeral=True)

    @econsadmin.error
    async def admin_error(self, interaction:discord.Interaction, error:app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingAnyRole):
            embed = discord.Embed(title="Missing Permissions!",
                                  description="You do not have the role/permission to use this command.",
                                  color=discord.Color.brand_red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            print(error)

    @app_commands.command(name="econs-leaderboard", description="Get leaderboard for economy")
    async def econsleaderboard(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        async with self.bot.economy_pool.acquire() as conn:
            rows = await conn.execute('''SELECT * FROM economydb ORDER BY money DESC LIMIT 10''')
            results = await rows.fetchall()
        results_list = [f"<@{result['user_id']}> - `🪙{result['money']}`" for result in results]
        resuls_final = "\n- ".join(results_list)
        embed = discord.Embed(title="Economy Leaderboard",
                              description=f">>> 1. {resuls_final}",
                              color=discord.Color.blurple())
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.followup.send(embed=embed)
    @app_commands.command(name="fish", description="Fish for catbucks!")
    @app_commands.checks.cooldown(1, 180)
    async def fish(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        earned = randint(80, 150)
        if earned >= 100 :
            final_response = "You caught the fish!"
            async with self.bot.economy_pool.acquire() as conn:
                await conn.execute('''INSERT INTO economydb (user_id, money) VALUES (?, ?)
                                ON CONFLICT(user_id) DO UPDATE SET money = excluded.money''', (interaction.user.id, earned))
                await conn.commit()
        else:
            final_response = "The fish got away!"
        await interaction.followup.send(f"Ooh! You feel something on your rod", ephemeral=True)
        await asyncio.sleep(0.75)
        await interaction.followup.send(f"It's now or never!", ephemeral=True)
        await asyncio.sleep(0.75)
        embed = discord.Embed(title="Awww man" if earned < 100 else "Let's go!",
                              description=f"```{final_response}```{f"\nYou caught **🪙{earned} catbucks!**" if earned > 100  else ""}",
                              color=discord.Color.brand_green() if earned > 100 else discord.Color.brand_red())
        embed.set_author(name=f"@{interaction.user}", icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @fish.error
    async def fish_error(self, interaction:discord.Interaction, error:app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed =discord.Embed(title="Cooldown!",
                                 description=f"Try again <t:{int(time.time()) + int(error.retry_after)}:R>!",
                                 color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            print(error)
            

async def setup(bot:commands.Bot):
    await bot.add_cog(EconomyCog(bot))
