import discord
from discord import app_commands
from discord.ext import commands

from data import config

class SetupView(discord.ui.View):
    def __init__(self, cog: "DiscordCog"):
        super().__init__(timeout=None)
        self.cog = cog
        self.current_page = 0

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.green)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        next_embed = self.cog.dc_embed_for_setup(self.current_page)

        if next_embed:
            await interaction.response.send_message(embed=next_embed, view=self, ephemeral=True)
        else:
            await interaction.response.send_message("Setup complete!", embed=None, view=None, ephemeral=True)


class DiscordCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    dc = app_commands.Group(name="dc", description="Discord commands", guild_ids=[config.GUILD_ID])

    def dc_embed_for_setup(self, embed_id: int):
        if embed_id == 0:
            return discord.Embed(
                title=f"{config.BOT_NAME} Setup",
                description=(
                    f"Thank you for using {config.BOT_NAME} bot!\n"
                    "This is initial set up for the bot. Just follow instructions as you go.\n\n"
                    "I was built by **Echodevlog**. Don't forget to follow his socials!\n\n"
                    "When you're ready, press the button below 👇."
                ),
                color=discord.Color.orange()
            )
        elif embed_id == 1:
            return discord.Embed(
                title="Step 2: Permissions",
                description="Please ensure the bot has 'Administrator' permissions for full functionality.",
                color=discord.Color.blue()
            )
        return None

    @app_commands.command(name="setup", description="Initial set up for the bot")
    @app_commands.guilds(config.GUILD_ID)
    async def dc_setup(self, interaction: discord.Interaction):
        view = SetupView(self)
        embed = self.dc_embed_for_setup(0)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)



async def setup(bot: commands.Bot):
    await bot.add_cog(DiscordCog(bot))