import discord
from discord.ext import commands

class APIConnections(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def valid_server_check(self):
        pass

async def setup(bot: commands.Bot):
    await bot.add_cog(APIConnections(bot))