import os
from datetime import datetime
from zoneinfo import ZoneInfo
import json

from utils.discord_tools import discord_object_converter
from data import config
from utils.tools import get_current_datetime

# === .env Functions ===
def env_validation():
    if not config.BOT_TOKEN:
        raise ValueError(f"❌ CRITICAL ERROR: Your BOT_TOKEN is missing from the .env file!")
    if not config.GUILD_ID:
        raise ValueError(f"❌ CRITICAL ERROR: Your GUILD_ID is missing from the .env file!")


# === Data Functions ===
def create_data_file():
    if config.DATA_FILE[5:len(config.DATA_FILE)] not in os.listdir("data"):
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

        with open(config.DATA_FILE, "w") as data_file:
            json.dump(default_data, data_file, indent=4)

async def read_data_file():
    try:
        with open(config.DATA_FILE, "r") as file:
            saved_data = json.load(file)

            # Settings
            config.setup_completed = saved_data["settings"]["setup_completed"]
            config.online_notification = saved_data["settings"]["online_notifications"]
            config.vote_notification = saved_data["settings"]["vote_notifications"]
            config.server_name = saved_data["settings"]["server_name"]

            if saved_data["settings"]["timezone"] is None:
                config.timezone = None
            else:
                config.timezone = ZoneInfo(saved_data["settings"]["timezone"])

            if saved_data["settings"]["vote_time"] is None:
                config.vote_time = None
            else:
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

            return True

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        if config.notifications_channel:
            await config.notifications_channel.send("⚠️ My data file was corrupted or missing. I'm creating a new one. Please go through a new setup process using `/setup`.")

        if os.path.exists(config.DATA_FILE):
            os.remove(config.DATA_FILE)

        create_data_file()
        config.setup_completed = False

        return False

def update_data(search_type : str, search : str, data : int | None | bool | str):
    with open(config.DATA_FILE, "r") as file:
        file_data = json.load(file)

    file_data[search_type][search] = data

    with open(config.DATA_FILE, "w") as file:
        json.dump(file_data, file, indent=4)


# === Log Functions ===
def create_log_file():
    with open(config.LOG_FILE, "w") as log_file:
        log_file.write(f"====== {config.BOT_NAME} ======")
    add_log("Log file created.")

def add_log(log_str):
    if os.path.exists(config.LOG_FILE):
        write_str = ""
        if "\n" in log_str:
            log_str = log_str[1:len(log_str)]
            write_str = "\n"

        time = get_current_datetime().strftime("[%d-%m-%Y] [%H:%M:%S]")

        write_str = write_str + time + " " +  log_str

        with open(config.LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write("\n" + write_str)

        print(write_str)
    else:
        create_log_file()
        print(f"\nError: Unable to save {log_str} in {config.LOG_FILE} do to the file not existing! Creating new {config.LOG_FILE}!")
