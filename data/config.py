import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from datetime import datetime

load_dotenv()

# About this bot
BOT_TOKEN : str | None = os.getenv("BOT_TOKEN")
env_guild_id = os.getenv("GUILD_ID")
GUILD_ID : int | None = int(env_guild_id) if env_guild_id else None
BOT_NAME : str = "MinePulse"
VERSION : int = 0
setup_completed : bool = False

bot : commands.Bot | None = None
guild : discord.Object | None = None

# File paths
DATA_FILE = "data/data.json"
LOG_FILE = "data/bot.log"

# Enabled functions
online_notification : bool = False
vote_notification : bool = False

# Public variables
ONLINE_NOTIFICATION_INTERVAL : int = 120 # (in seconds)
VOTE_NOTIFICATION_INTERVAL : int = 24 # (in hours)
bot_startup_time : datetime | None = None
bot_state : str | None = ""
timezone : str | None = None
vote_time : datetime | None = None

EXTRA_SERVER_INFO : bool = False # adds servers IP and platform to online notification message

# Minecraft variables
server_name : str | None = None

# Text Channels - Objects
notifications_channel : discord.TextChannel | None = None

# Roles - objects
staff_role : discord.Role | None = None
online_role : discord.Role | None = None
vote_role : discord.Role | None = None

# Messages
online_message : discord.Message | None = None
vote_message : discord.Message | None = None

# MH API
connections_succeeded_count : int = 0
connections_failed_count : int = 0
