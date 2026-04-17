from datetime import datetime
from zoneinfo import ZoneInfo
import json

from utils.discord_tools import discord_object_converter
from data import config


def env_validation():
    if not config.BOT_TOKEN:
        raise ValueError(f"❌ CRITICAL ERROR: Your BOT_TOKEN is missing from the .env file!")
    if not config.GUILD_ID:
        raise ValueError(f"❌ CRITICAL ERROR: Your GUILD_ID is missing from the .env file!")

def create_data_file():
    default_data = {
        "settings" : {
            "setup_completed" : False,
            "online_notifications" : False,
            "vote_notifications" : False,
            "server_name" : None,
            "timezone" : None,
            "vote_time" : None
        },
        "text_channels" : {
            "notification_channel_id" : None
        },
        "roles" : {
            "staff_role_id" : None,
            "online_role_id" : None,
            "vote_role_id" : None
        },
        "messages" : {
            "online_message_id" : None,
            "vote_message_id" : None
        }
    }

    with open(config.DATA_FILE, "w") as file:
        json.dump(default_data, file, indent=4)

async def read_data_file():
    # if any error happens ... delete data.json and create new one -> "Corrupted Data"

    with open(config.DATA_FILE, "r") as file:
        saved_data = json.load(file)

        # Settings
        config.setup_completed = saved_data["settings"]["setup_completed"]
        config.online_notification = saved_data["settings"]["online_notifications"]
        config.vote_notification = saved_data["settings"]["vote_notifications"]
        config.server_name = saved_data["settings"]["server_name"]
        config.timezone = ZoneInfo(saved_data["settings"]["timezone"])
        config.vote_time = datetime.strptime(saved_data["settings"]["vote_time"], "%H:%M:%S").time()

        # Text Channels
        config.notifications_channel = await discord_object_converter(saved_data["text_channels"]["notification_channel_id"])

        # Roles
        config.staff_role = await discord_object_converter(saved_data["roles"]["staff_role_id"])
        config.online_role = await discord_object_converter(saved_data["roles"]["online_role_id"])
        config.vote_role = await discord_object_converter(saved_data["roles"]["vote_role_id"])

        # Messages
        config.online_message = await discord_object_converter(saved_data["messages"]["online_message_id"])
        config.vote_message = await discord_object_converter(saved_data["messages"]["vote_message_id"])

def update_data(search_type : str, search : str, data : int | None | bool | str):
    with open(config.DATA_FILE, "r") as file:
        file_data = json.load(file)

    file_data[search_type][search] = data

    with open(config.DATA_FILE, "w") as file:
        json.dump(file_data, file, indent=4)
