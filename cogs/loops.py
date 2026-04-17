from multiprocessing.spawn import old_main_modules

import discord
from discord.ext import commands, tasks

from utils.api_calls import get_api_data
from utils.data_manager import update_data
from utils.tools import time_conversion
from utils.health import check_server_health, check_server_online

from data import config


class Loops(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_connections_cog = self.bot.get_cog("APIConnections")
        self.old_player_count = 0
        self.old_state = False
        self.initial_send = False

    @tasks.loop(seconds=config.ONLINE_NOTIFICATION_INTERVAL)
    async def sever_online_loop(self):
        server_warning_info : str = ""

        data = await get_api_data()

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
                date_str = c_date.replace("-", " ")
                days, hours, minutes, seconds = time_conversion(time)

                embed = discord.Embed(
                    title=f"{name} is currently OFFLINE!",
                    description=f"Last online on the day: **`{date_str}`**, for total of: **`{days} days, {hours} h, {minutes} min, {seconds} s`**" + extra_server_info + server_warning_info,
                    color=discord.Color.red()
                )

            # Sending embed
            # true        true      false => server just got online
            if online and online != self.old_state:
                if config.online_message: await config.online_message.delete()
                config.online_message = await config.notifications_channel.send(content=config.online_role.mention, embed=embed)
                update_data("messages", "online_message_id", config.online_message.id)

            #    true       true      true => server was online in the previous check as well => check if player count changed
            elif online and online == self.old_state:
                if player_count != self.old_player_count:
                    await config.online_message.edit(content=config.online_role.mention, embed=embed)

            #     false            false        true => server just got offline
            elif not online and not online != self.old_state:
                if config.online_message:
                    await config.online_message.edit(content=config.online_role.mention, embed=embed)
                else:
                    config.online_message = await config.notifications_channel.send(content=config.online_role.mention, embed=embed)
                    update_data("messages", "online_message_id", config.online_message.id)

            #      false          false        false => server was offline in the previous check as well
            elif not online and not online == self.old_state and not self.initial_send:
                if config.online_message:
                    await config.online_message.edit(content=config.online_role.mention, embed=embed)
                else:
                    config.online_message = await config.notifications_channel.send(content=config.online_role.mention, embed=embed)
                    update_data("messages", "online_message_id", config.online_message.id)
                self.initial_send = True

            self.old_state = online
            self.old_player_count = player_count


    @tasks.loop(time=config.vote_time.replace(tzinfo=config.timezone))
    async def vote_MH_loop(self):
        embed = discord.Embed(
            title="Vote Reminded!",
            description="Don't forget to vote for MineHut to earn free credits!"
                        "\n[VOTE HERE!](https://findmcserver.com/server/minehut)",
            color=discord.Color.blue()
        )

        if config.vote_notification is not None:
            await config.vote_message.delete()
        config.vote_message = await config.notifications_channel.send(content=config.vote_role.mention, embed=embed)
        update_data("messages", "vote_message_id", config.vote_message.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Loops(bot))