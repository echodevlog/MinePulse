import os
from dotenv import load_dotenv
import discord

# VARIABLES
BOT_TOKEN : str | None = None
GUILD_ID : int | None = None
BOT_NAME : str = "MinePulse"

# Roles - objects
STAFF_ROLE : discord.Role | None = None

# Channels - Objects

def load_env():
    global BOT_TOKEN
    global GUILD_ID

    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID"))
