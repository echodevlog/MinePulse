from discord.ext import commands
import requests
from data import config

class APIConnections(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_api_data(self):
        if config.SERVER_NAME is None:
            return False

        minehut_api = f"https://api.minehut.com/server/{config.SERVER_NAME}?byName=True"

        response = requests.get(minehut_api)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return False


    def valid_server_checker(self):
        data = self.get_api_data()

        if data:
            server = data["server"]

            if server is None: return False
            elif isinstance(server, dict): return True
            else: return False

        else:
            return False

async def setup(bot: commands.Bot):
    await bot.add_cog(APIConnections(bot))