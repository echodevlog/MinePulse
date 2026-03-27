import os
from dotenv import load_dotenv

# VARIABLES
BOT_TOKEN : str | None = None
GUILD_ID : int | None = None

def load_env():
    global BOT_TOKEN
    global GUILD_ID

    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID"))
