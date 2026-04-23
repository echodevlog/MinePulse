import discord
from discord import app_commands
from discord.ext import commands

from data import config
from utils.tools import get_current_datetime

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    bot = app_commands.Group(name="bot", description="Bot related commands", guild_ids=[config.GUILD_ID])
    mc = app_commands.Group(name="mc", description="Minecraft related commands", guild_ids=[config.GUILD_ID])
    server = app_commands.Group(name="server", description="Server related commands", guild_ids=[config.GUILD_ID], parent=mc)

    @bot.command(name="state", description="Show bot's current state")
    async def bot_state(self, interaction: discord.Interaction):
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

async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))