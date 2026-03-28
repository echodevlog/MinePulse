import os
from datetime import datetime
from dotenv import load_dotenv
import discord

# About this bot
BOT_TOKEN : str | None = None
GUILD_ID : int | None = None
BOT_NAME : str = "MinePulse"

# Minecraft variables
SERVER_NAME : str | None = None

# Roles - objects
STAFF_ROLE : discord.Role | None = None

# Channels - Objects
NOTIFICATIONS_CHANNEL : discord.TextChannel | None

# Enabled functions
online_notification : bool = False
vote_notifications : bool = False
TIMEZONE : str | None = None
VOTE_TIME : datetime | None= None

def load_env():
    global BOT_TOKEN
    global GUILD_ID

    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID"))
