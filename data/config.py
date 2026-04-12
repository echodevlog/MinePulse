import json
import os
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands

# About this bot
BOT_TOKEN : str | None = None
GUILD_ID : int | None = None
BOT_NAME : str = "MinePulse"
setup_completed : bool = False

bot : commands.Bot | None = None
guild : discord.Object | None = None

# Minecraft variables
SERVER_NAME : str | None = None

# File paths
data_file = "data/data.json"
logs_file = "data/logs.txt"

# Enabled functions
online_notifications : bool = False
vote_notifications : bool = False
TIMEZONE : str | None = None
VOTE_TIME : datetime | None= None

# Text Channels - Objects
NOTIFICATIONS_CHANNEL : discord.TextChannel | None = None

# Roles - objects
STAFF_ROLE : discord.Role | None = None
ONLINE_ROLE : discord.Role | None = None
VOTE_ROLE : discord.Role | None = None

# Messages
online_message : discord.Message | None = None
vote_message : discord.Message | None = None

def set_bot(bot_obj):
    global bot, guild
    bot = bot_obj
    guild = bot.get_guild(GUILD_ID)

def load_env():
    global BOT_TOKEN
    global GUILD_ID

    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID"))

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

    with open(data_file, "w") as file:
        json.dump(default_data, file, indent=4)

async def read_data_file():
    global setup_completed, online_notifications, vote_notifications, SERVER_NAME, TIMEZONE, VOTE_TIME
    global NOTIFICATIONS_CHANNEL
    global STAFF_ROLE, ONLINE_ROLE, VOTE_ROLE
    global online_message, vote_message

    with open(data_file, "r") as file:
        saved_data = json.load(file)

        # Settings
        setup_completed = saved_data["settings"]["setup_completed"]
        online_notifications = saved_data["settings"]["online_notifications"]
        vote_notifications = saved_data["settings"]["vote_notifications"]
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
    print(f"Changing: {search}, with data: {data}, with a type of: {type(data)}")

    with open(data_file, "r") as file:
        file_data = json.load(file)

    file_data[search_type][search] = data

    with open(data_file, "w") as file:
        json.dump(file_data, file, indent=4)

async def discord_object_converter(data_id : int | None):
    output_obj = None
    if data_id is None:
        return output_obj

    if bot.get_channel(data_id):
        output_obj = bot.get_channel(data_id)

    elif guild.get_role(data_id) is not None:
        output_obj = guild.get_role(data_id)

    elif NOTIFICATIONS_CHANNEL:
        try:
            output_obj = await NOTIFICATIONS_CHANNEL.fetch_message(data_id)
        except discord.NotFound:
            pass

    return output_obj

async def start_loops():
    loops_cog = bot.get_cog("Loops")

    if loops_cog:
        if online_notifications:
            loops_cog.sever_online_loop.start()
            print("Starting online loop")

        elif vote_notifications:
            loops_cog.vote_MH_loop.start()
            print("Starting vote loop")

        else:
            print("No loops activated")