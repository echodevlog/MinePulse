import discord
from discord.ext import commands, tasks

from data import config

class Loops(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_connections_cog = self.bot.get_cog("APIConnections")
        self.old_player_count = 0
        self.initial_send = False

    @tasks.loop(seconds=config.online_notification_interval)
    async def sever_online_loop(self):
        extra_server_info : str = ""

        if self.api_connections_cog:
            data = self.api_connections_cog.get_api_data()

            if data:
                if not self.check_server_health(data):
                    extra_server_info = "\n> **Please check your server's health. We detected that something might be wrong!**"


                name = data["server"]["name"]
                daily_online_time = data["server"]["daily_online_time"]
                boosts = data["server"]["boosts"]
                online = data["server"]["online"]
                max_players = data["server"]["maxPlayers"]
                player_count = data["server"]["playerCount"]


                # Embed content
                if online:
                    embed = discord.Embed(
                        title=f"{name} is currently ONLINE!",
                        description=f"> Current player count: **`{player_count}/{max_players}`**"
                                    f"\n > Boosts: **`{boosts}`**" + extra_server_info,
                        color=discord.Color.green()
                    )

                else:
                    c_date, time = list(daily_online_time.items())[0]
                    days, hours, minutes, seconds = config.time_conversion(time)

                    embed = discord.Embed(
                        title=f"{name} is currently OFFLINE!",
                        description=f"Last online on the day: **`{c_date}`**, for total of: **`{days} days, {hours} h, {minutes} min, {seconds} s`**" + extra_server_info,
                        color=discord.Color.red()
                    )

                # Sending embed
                if config.online_message is None:
                    config.online_message = await config.NOTIFICATIONS_CHANNEL.send(content=config.ONLINE_ROLE.mention, embed=embed)
                    config.update_data("messages", "online_message_id", config.online_message.id)
                else:
                    if not self.initial_send or self.old_player_count < player_count:
                        await config.online_message.edit(content=config.ONLINE_ROLE.mention, embed=embed)


    @tasks.loop(hours=config.vote_notification_interval)
    async def vote_MH_loop(self):
        pass

    def check_server_health(self, data):
        print("check_server_health() is in progress")

        server_is_healthy : bool = True
        embed : discord.Embed | None = None

        visibility = data["server"]["visibility"]
        suspended = data["server"]["suspended"]
        expired = data["server"]["expired"]

        deleted = data["server"]["deleted"]
        hidden = data["server"]["hidden"]

        # Server Deletion
        deletion_started = data["server"]["deletion"]["started"]
        deletion_started_at = data["server"]["deletion"]["started_at"]
        deletion_reason = data["server"]["deletion"]["reason"]
        deletion_metadata_description = data["server"]["deletion"]["metadata"]["description"]
        deletion_metadata_last_unflagged = data["server"]["deletion"]["metadata"]["last_unflagged"]
        deletion_completed = data["server"]["deletion"]["completed"]
        deletion_completed_at = data["server"]["deletion"]["completed_at"]

        # Storage Completed
        deletion_storage_completed = data["server"]["deletion"]["storage_completed"]
        deletion_storage_completed_at = data["server"]["deletion"]["storage_completed_at"]

        if not visibility:
            embed = discord.Embed(
                title="⚠️ Server is currently not VISIBLE!",
                description=f"We detected that your server is currently **not visible** on MineHut"
                            f"\n> Visibility: **`{visibility}`**",
                color=discord.Color.orange()
            )

        elif suspended:
            embed = discord.Embed(
                title="❌ Server is SUSPENED!",
                description=f"We detected that your server is currently **suspended** on MineHut"
                            f"\n> Suspended: **`{suspended}`**",
                color=discord.Color.red()
            )

        elif expired:
            embed = discord.Embed(
                title="❌ Server is EXPIRED!",
                description=f"We detected that your server is currently **expired** on MineHut"
                            f"\n> Expired: **`{expired}`**",
                color=discord.Color.red()
            )

        elif deleted or deletion_started or deletion_completed:
            converted_dst = config.date_conversion(deletion_started_at)
            converted_last_unflagged = config.date_conversion(deletion_metadata_last_unflagged)
            converted_dca = config.date_conversion(deletion_completed_at)

            embed = discord.Embed(
                title="❌ Server is DELETED!",
                description=f"We detected that your server is currently **deleted** on MineHut"
                            f"\n> Deletion started: **`{deletion_started}`**"
                            f"\n> Deletion started at: **`{converted_dst}`**"
                            f"\n> Reason: **`{deletion_reason}`**"
                            f"\n> Metadata description: **`{deletion_metadata_description}`**"
                            f"\n> Metadata last unflagged: **`{converted_last_unflagged}`**"
                            f"\n> Deletion completed: **`{deletion_completed}`**"
                            f"\n> Deletion completed at: **`{converted_dca}`**"
                            f"\n> **`{deleted}`**"
                            f"\n> **`{deleted}`**"
                            f"\n> Deleted: **`{deleted}`**",
                color=discord.Color.red()
            )

        elif deletion_storage_completed:
            converted_sca = config.date_conversion(deletion_storage_completed_at)

            embed = discord.Embed(
                title="❌ Your server's storage is COMPLETED!",
                description=f"We detected that your server's storage is currently **completed**."
                            f"\n> Storage completed: **`{deletion_storage_completed}`**"
                            f"\n> Storage completed at: **`{converted_sca}`**",
                color=discord.Color.red()
            )

        elif hidden:
            embed = discord.Embed(
                title="❌ Your server is HIDDEN!",
                description=f"We detected that your server is currently **hidden** on MineHut."
                            f"\n> Hidden: **`{hidden}`**",
                color=discord.Color.red()
            )

        if embed is not None and config.NOTIFICATIONS_CHANNEL is not None:
            config.NOTIFICATIONS_CHANNEL.send(content=config.STAFF_ROLE.mention, embed=embed)
            server_is_healthy = False

        return server_is_healthy

    def check_server_online(self, data):
        online = data["server"]["online"]

        if online:
            return True
        else:
            return False


async def setup(bot: commands.Bot):
    await bot.add_cog(Loops(bot))