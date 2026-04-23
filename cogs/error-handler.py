import discord
from discord.ext import commands
import traceback

from utils.data_manager import add_log

class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandNotFound):
            return

        error_message = f"Command `{interaction.command}` failed: {traceback.format_exc()}."
        add_log(error_message)

        await interaction.response.send_message("⚠️ Sorry, an error has occurred.")


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))