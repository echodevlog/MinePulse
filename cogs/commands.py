import discord
from discord import app_commands
from discord.ext import commands

from data import config
from utils.tools import get_current_datetime, date_conversion, time_conversion
from utils.api_calls import get_api_data

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    bot = app_commands.Group(name="bot", description="Bot related commands", guild_ids=[config.GUILD_ID])
    mc = app_commands.Group(name="mc", description="Minecraft related commands", guild_ids=[config.GUILD_ID])
    server = app_commands.Group(name="server", description="Server related commands", guild_ids=[config.GUILD_ID], parent=mc)

    @bot.command(name="state", description="Show bot's current state")
    async def bot_state(self, interaction: discord.Interaction):
        if config.staff_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        now = get_current_datetime()
        uptime = now - config.bot_startup_time

        uptime_seconds = int(uptime.total_seconds())
        days, reminder = divmod(uptime_seconds, 86400)
        hours, reminder = divmod(reminder, 3600)
        minutes, seconds = divmod(reminder, 60)

        embed = discord.Embed(
            title=f"{config.BOT_NAME} State",
            description=f"Version: **{config.VERSION}**"
                        f"\nState: **{config.bot_state}**"
                        f"\nUptime: **{days} days, {hours}h, {minutes} min, {seconds} s**"
                        
                        f"\n\nSETTINGS"
                        f"\n - General"
                        f"\n> Setup completed: **{config.setup_completed}**"
                        f"\n> Extra server info: **{config.EXTRA_SERVER_INFO}**"
                        f"\n> Staff role: **{config.staff_role.mention}**"
                        f"\n> Notification channel: **{config.notifications_channel.mention}**"
                        f"\n> MC server name: **{config.server_name}**"

                        f"\n\n- MC (Online) Notification Settings"
                        f"\n> MC (online) notification: **{config.online_notification}**"
                        f"\n> MC (online) notification role: **{config.online_role.mention}**"
                        
                        f"\n\n- Vote Notification Settings"
                        f"\n> Vote notification: **{config.vote_notification}**"
                        f"\n> Vote notification role: **{config.vote_role.mention}**"
                        f"\n> Vote time: **{config.vote_time}**"
                        f"\n> Timezone: **{config.timezone}**"

                        f"\n\nMINEHUT API"
                        f"\n> MH API connection seconded: **{config.connections_succeeded_count}**"
                        f"\n> MH API connection failed: **{config.connections_failed_count}**",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.command(name="log", description="Read bot's log file")
    async def bot_logs(self, interaction: discord.Interaction):
        if config.staff_role not in interaction.user.roles:
            return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        with open(config.LOG_FILE, "r") as log_file:
            data = log_file.read()

        embed = discord.Embed(
            title=f"{config.BOT_NAME}'s log file:",
            description=f"```{data}```",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="about", description="Information about this bot")
    @app_commands.guilds(config.GUILD_ID)
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"Hi! My name is MinePulse",
            description="I am a custom build bot from creator called **[EchoDevLog](https://www.youtube.com/@EchoDevLog)**. I'm here to help you with your Minecraft server hosted on MineHut!"
                        "\nIf set up correctly I will send a notification when your server goes online. If you just invited me, you can begin setting me up using `/setup` command."
                        "\n\nHope I'll be at a great use for you :)",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @server.command(name="ip", description="Shows MC server IP")
    async def mc_server_ip(self, interaction: discord.Interaction):
        data = await get_api_data()
        if data:
            online = data["server"]["online"]
            current_player_count = data["server"]["playerCount"]
        else:
            current_player_count = online = "Data currently unavailable :("

        embed = discord.Embed(
            title=f"{config.server_name} IP",
            description=f"Here's info your looking for:"
                        f"\n> Server IP (java): **{config.server_name}.minehut.gg**"
                        f"\n> Port: **25565**"
                        f"\n> Online: **{online}**"
                        f"\n> Current play count: **{current_player_count}**",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @server.command(name="stats", description="MC server statistics")
    async def mc_server_stats(self, interaction: discord.Interaction):
        data = await get_api_data()
        categories_str = "No categories"

        if data:
            name = data["server"]["name"]
            creation = data["server"]["creation"]
            creation = date_conversion(creation)
            platform = data["server"]["platform"]
            motd = data["server"]["motd"]
            categories = data["server"]["categories"]
            server_plan = data["server"]["server_plan"]
            last_online = data["server"]["last_online"]
            last_online = date_conversion(last_online)
            joins = data["server"]["joins"]
            boosts = data["server"]["boosts"]
            online = data["server"]["online"]
            maxPlayers = data["server"]["maxPlayers"]
            playerCount = data["server"]["playerCount"]

            if categories:
                for category in categories:
                    category = str(category)
                    categories_str += " " + category


        embed = discord.Embed(
            title=f"{config.server_name} statistics",
            description=f"\nName: **{name}**"
                        f"\nMOTD: **{motd}**"
                        f"\nPlatform: **{platform}**"
                        f"\nCreation: **{creation}**"
                        f"\nCategories: **{categories_str}**"
                        f"\nServer_plan: **{server_plan}**"
                        f"\nLast online: **{last_online}**"
                        f"\nJoins **{joins}**"
                        f"\nBoosts: **{boosts}**"
                        f"\nOnline: **{online}**"
                        f"\nMax players **{maxPlayers}**"
                        f"\nPlayer count: **{playerCount}**",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))