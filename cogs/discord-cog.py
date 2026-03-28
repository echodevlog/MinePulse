import discord
from discord import app_commands, Interaction
from discord.ext import commands

from data import config

class RoleDropdown(discord.ui.RoleSelect):
    def __init__(self, parent_view: "SetupView"):
        super().__init__(placeholder="Search for a role...", min_values=1, max_values=1)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        selected_role = self.values[0]
        self.parent_view.selected_staff_role = selected_role
        config.STAFF_ROLE = selected_role

        await self.parent_view.continue_callback(interaction)


class SetupDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="General Chat", description="Use the general channel for logs"),
            discord.SelectOption(label="Admin Logs", description="Use a private staff channel"),
        ]
        super().__init__(placeholder="Select staff role ...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Selected: {self.values[0]}", ephemeral=True)


class SetupView(discord.ui.View):
    def __init__(self, cog: "DiscordCog"):
        super().__init__(timeout=None)
        self.cog : cog = cog
        self.current_page : int = 0
        self.selected_staff_role : discord.Role | None = None
        self.create_page()

    def create_page(self):
        self.clear_items()

        if self.current_page == 0:
            self.add_item(discord.ui.Button(label="YouTube", style=discord.ButtonStyle.link, url="https://www.youtube.com/@EchoDevlog"))
            self.add_item(discord.ui.Button(label="Discord Server", style=discord.ButtonStyle.link, url="https://discord.gg/example"))

        elif self.current_page == 1:
            self.add_item(RoleDropdown(parent_view=self))

        if self.current_page != 1:
            if self.cog.dc_embed_for_setup(self.current_page + 1) is not None:
                continue_btn = discord.ui.Button(label="Continue", style=discord.ButtonStyle.green, row=4)
                continue_btn.callback = self.continue_callback
                self.add_item(continue_btn)
            else:
                finish_btn = discord.ui.Button(label="Finish", style=discord.ButtonStyle.blurple, row=4)
                finish_btn.callback = self.continue_callback
                self.add_item(finish_btn)

    async def continue_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.current_page += 1

        self.create_page()
        next_embed = self.cog.dc_embed_for_setup(self.current_page)

        if next_embed:
            await interaction.edit_original_response(embed=next_embed, view=self)
        else:
            await interaction.edit_original_response(content="✅ Setup complete!", embed=None, view=None)
            self.stop()


class DiscordCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    dc = app_commands.Group(name="dc", description="Discord commands", guild_ids=[config.GUILD_ID])

    def dc_embed_for_setup(self, embed_page: int):
        if embed_page == 0:
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
        elif embed_page == 1:
            return discord.Embed(
                title="Step 1: Staff",
                description="Please select which role is your a staff role in the dropdown below:",
                color=discord.Color.orange()
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