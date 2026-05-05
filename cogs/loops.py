import discord
from discord.ext import commands, tasks

from utils.api_calls import get_api_data
from utils.data_manager import update_data
from utils.tools import time_conversion, get_current_datetime
from utils.health import check_server_health

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
        if not config.setup_completed:
            return

        if not config.online_notification:
            self.sever_online_loop.stop()
            return

        server_warning_info : str = "\nSeems like server is behaving normally."

        data = await get_api_data()

        if data:
            if not await check_server_health(data):
                server_warning_info = "\n> **Please check your server's health. We detected that something might be wrong!**"

            name = data["server"]["name"]
            boosts = data["server"]["boosts"]
            online = data["server"]["online"]
            max_players = data["server"]["maxPlayers"]
            player_count = data["server"]["playerCount"]
            server_platform = data["server"]["platform"]

            if data.get("server").get("daily_online_time"):
                daily_online_time = data["server"]["daily_online_time"]
            else:
                daily_online_time = None

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
                if daily_online_time:
                    c_date, time = list(daily_online_time.items())[0]
                    date_str = c_date.replace("-", " ")
                    days, hours, minutes, seconds = time_conversion(time)
                    description = f"Last online on the day: **`{date_str}`**, for total of: **`{days} days, {hours} h, {minutes} min, {seconds} s`**"
                else:
                    description = f"Last online on the day: **No information, sorry :(**"

                server_warning_info = ""
                current_time = get_current_datetime()

                embed = discord.Embed(
                    title=f"{name} is currently OFFLINE!",
                    description=f"{description}"
                                f"\nAt: **`{current_time.time().strftime("%H:%M")}`**" + extra_server_info + server_warning_info,
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


    @tasks.loop(time=config.vote_time.timetz())
    async def vote_MH_loop(self):
        if not config.setup_completed:
            return

        if not config.vote_notification:
            self.vote_MH_loop.stop()
            return

        embed = discord.Embed(
            title="Vote Reminder!",
            description="Don't forget to vote for MineHut to earn free credits!"
                        "\n[VOTE HERE!](https://findmcserver.com/server/minehut)",
            color=discord.Color.blue()
        )

        if config.vote_notification is not None and config.vote_message:
            await config.vote_message.delete()
        config.vote_message = await config.notifications_channel.send(content=config.vote_role.mention, embed=embed)
        update_data("messages", "vote_message_id", config.vote_message.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Loops(bot))