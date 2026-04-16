import os
from dotenv import load_dotenv
from datetime import datetime
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

    global setup_completed, online_notification, vote_notification, SERVER_NAME, TIMEZONE, VOTE_TIME
    global NOTIFICATIONS_CHANNEL
    global STAFF_ROLE, ONLINE_ROLE, VOTE_ROLE
    global online_message, vote_message

    with open(config.DATA_FILE, "r") as file:
        saved_data = json.load(file)

        # Settings
        setup_completed = saved_data["settings"]["setup_completed"]
        online_notification = saved_data["settings"]["online_notifications"]
        vote_notification = saved_data["settings"]["vote_notifications"]
        SERVER_NAME = saved_data["settings"]["server_name"]
        TIMEZONE = saved_data["settings"]["timezone"]
        VOTE_TIME = datetime.strptime(saved_data["settings"]["vote_time"], "%H:%M:%S").time()

        # Text Channels
        NOTIFICATIONS_CHANNEL = await discord_object_converter(saved_data["text_channels"]["notification_channel_id"])

        # Roles
        STAFF_ROLE = await discord_object_converter(saved_data["roles"]["staff_role_id"])
        ONLINE_ROLE = await discord_object_converter(saved_data["roles"]["online_role_id"])
        VOTE_ROLE = await discord_object_converter(saved_data["roles"]["vote_role_id"])

        # Messages
        online_message = await discord_object_converter(saved_data["messages"]["online_message_id"])
        vote_message = await discord_object_converter(saved_data["messages"]["vote_message_id"])

def update_data(search_type : str, search : str, data : int | None | bool | str):
    with open(config.DATA_FILE, "r") as file:
        file_data = json.load(file)

    file_data[search_type][search] = data

    with open(config.DATA_FILE, "w") as file:
        json.dump(file_data, file, indent=4)
