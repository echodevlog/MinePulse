import discord
from discord.ext import commands, tasks

from utils.data_manager import update_data
from utils.tools import time_conversion
from utils.health import check_server_health

from data import config


class Loops(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_connections_cog = self.bot.get_cog("APIConnections")
        self.old_player_count = 0
        self.initial_send = False

    @tasks.loop(seconds=config.ONLINE_NOTIFICATION_INTERVAL)
    async def sever_online_loop(self):
        server_warning_info : str = ""

        if self.api_connections_cog:
            data = self.api_connections_cog.get_api_data()

            if data:
                if not await check_server_health(data):
                    server_warning_info = "\n> **Please check your server's health. We detected that something might be wrong!**"


                name = data["server"]["name"]
                daily_online_time = data["server"]["daily_online_time"]
                boosts = data["server"]["boosts"]
                online = data["server"]["online"]
                max_players = data["server"]["maxPlayers"]
                player_count = data["server"]["playerCount"]
                server_platform = data["server"]["platform"]

                if config.EXTRA_SERVER_INFO:
                    extra_server_info = f"\n\n> Join our server at **`{config.server_name}.minehut.gg`** via **`{server_platform}`** edition!"
                else:
                    extra_server_info = ""

                # Embed content
                if online:
                    embed = discord.Embed(
                        title=f"{name} is currently ONLINE!",
                        description=f"> Current player count: **`{player_count}/{max_players}`**"
                                    f"\n > Boosts: **`{boosts}`**" + extra_server_info + server_warning_info,
                        color=discord.Color.green()
                    )

                else:
                    c_date, time = list(daily_online_time.items())[0]
                    days, hours, minutes, seconds = time_conversion(time)

                    embed = discord.Embed(
                        title=f"{name} is currently OFFLINE!",
                        description=f"Last online on the day: **`{c_date}`**, for total of: **`{days} days, {hours} h, {minutes} min, {seconds} s`**" + extra_server_info + server_warning_info,
                        color=discord.Color.red()
                    )

                # Sending embed
                if config.online_message is None:
                    config.online_message = await config.notifications_channel.send(content=config.online_role.mention, embed=embed)
                    update_data("messages", "online_message_id", config.online_message.id)
                else:
                    if not self.initial_send or self.old_player_count < player_count:
                        await config.online_message.edit(content=config.online_role.mention, embed=embed)

    @tasks.loop(hours=config.VOTE_NOTIFICATION_INTERVAL)
    async def vote_MH_loop(self):
        embed = discord.Embed(
            title="Vote Reminded!",
            description="Don't forget to vote for MineHut to earn free credits"
                        "\n> [VOTE HERE!](https://findmcserver.com/server/minehut)",
            color=discord.Color.blue()
        )

        await config.notifications_channel.send(content=config.vote_role.mention, embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Loops(bot))