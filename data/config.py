import os
from datetime import datetime
from dotenv import load_dotenv
import discord

# About this bot
BOT_TOKEN : str | None = None
GUILD_ID : int | None = None
BOT_NAME : str = "MinePulse"
setup_completed : bool = False

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
NOTIFICATIONS_CHANNEL : discord.TextChannel | None

# Roles - objects
STAFF_ROLE : discord.Role | None = None
ONLINE_ROLE : discord.Role | None = None
VOTE_ROLE : discord.Role | None = None

# Messages
online_message : discord.Message | None = None
vote_message : discord.Message | None = None


def load_env():
    global BOT_TOKEN
    global GUILD_ID

    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID"))

def create_data_file():
    pass

def read_data_file():
    # saves data from data.json and converts it in to objects, then saves it in to config.py
    pass