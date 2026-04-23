import discord

import utils.tools
from data import config


async def check_server_health(data):
    server_is_healthy : bool = True
    embed : discord.Embed | None = None

    online = data["server"]["online"]

    suspended = data["server"]["suspended"]
    expired = data["server"]["expired"]

    deleted = data["server"]["deleted"]
    hidden = data["server"]["hidden"]

    # Server Deletion
    deletion_started = data["server"]["deletion"]["started"]
    deletion_started_at = data["server"]["deletion"]["started_at"]
    deletion_reason = data["server"]["deletion"]["reason"]

    try:
        deletion_metadata_description = data["server"]["deletion"]["metadata"]["description"]
        deletion_metadata_last_unflagged = data["server"]["deletion"]["metadata"]["last_unflagged"]
    except KeyError as e:
        deletion_metadata_description = "No information provided"
        deletion_metadata_last_unflagged = "No information provided"

    deletion_completed = data["server"]["deletion"]["completed"]
    deletion_completed_at = data["server"]["deletion"]["completed_at"]

    # Storage Completed
    deletion_storage_completed = data["server"]["deletion"]["storage_completed"]
    deletion_storage_completed_at = data["server"]["deletion"]["storage_completed_at"]

    if suspended:
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
        converted_dst = utils.tools.date_conversion(deletion_started_at)
        converted_last_unflagged = utils.tools.date_conversion(deletion_metadata_last_unflagged)
        converted_dca = utils.tools.date_conversion(deletion_completed_at)

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
                        f"\n> Deleted: **`{deleted}`**",
            color=discord.Color.red()
        )

    elif deletion_storage_completed:
        converted_sca = utils.tools.date_conversion(deletion_storage_completed_at)

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

    if embed is not None and config.notifications_channel is not None:
        await config.notifications_channel.send(content=config.staff_role.mention, embed=embed)
        server_is_healthy = False

    return server_is_healthy

def check_server_online(data):
    return data["server"]["online"]