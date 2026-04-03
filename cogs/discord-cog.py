import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime

from data import config


class RoleDropdown(discord.ui.RoleSelect):
    def __init__(self, parent_view: "SetupView", role_type: str):
        super().__init__(placeholder="Search for role ...", min_values=1, max_values=1)
        self.parent_view = parent_view
        self.role_type = role_type

    async def callback(self, interaction: discord.Interaction):
        selected_role = self.values[0]

        match self.role_type:
            case "STAFF_ROLE":
                self.parent_view.staff_role = selected_role
                config.STAFF_ROLE = selected_role
                config.update_data("roles", "staff_role_id", selected_role.id)
            case "ONLINE_ROLE":
                self.parent_view.online_role = selected_role
                config.ONLINE_ROLE = selected_role
                config.update_data("roles", "online_role_id", selected_role.id)
            case "VOTE_ROLE":
                self.parent_view.online_role = selected_role
                config.VOTE_ROLE = selected_role
                config.update_data("roles", "vote_role_id", selected_role.id)

        await self.parent_view.continue_callback(interaction)

class ChannelDropdown(discord.ui.ChannelSelect):
    def __init__(self, parent_view: "SetupView"):
        super().__init__(placeholder="Search for notification channel ...", min_values=1, max_values=1, channel_types=[discord.ChannelType.text])
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        selected_channel = self.values[0]
        self.parent_view.notification_channel = selected_channel
        config.NOTIFICATIONS_CHANNEL = selected_channel
        config.update_data("text_channels", "notification_channel_id", selected_channel.id)

        await self.parent_view.continue_callback(interaction)

class MineHutModal(discord.ui.Modal, title="Name of MineHut's server"):
    server_name = discord.ui.TextInput(
        label="What is your MineHut's server name?",
        placeholder="e. g. MyEpicMineHutServer",
        min_length=3,
        max_length=32,
        required=True
    )

    def __init__(self, parent_view: "SetupView"):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        if " " in self.server_name.value:
            return await interaction.response.send_message("❌ Error: MineHut server names cannot contain spaces. Please try again!", ephemeral=True)

        config.SERVER_NAME = self.server_name.value
        api_cog = self.parent_view.cog.bot.get_cog("APIConnections")
        if api_cog.valid_server_checker():
            self.parent_view.server_name = self.server_name.value
            config.update_data("settings", "server_name", self.server_name.value)
            await self.parent_view.continue_callback(interaction)

        else:
            config.SERVER_NAME = None
            return await interaction.response.send_message(f"❌ Error: I can't find provided server (by the name: **{self.server_name.value}**). Please provide valid MineHut server name!", ephemeral=True)

class FunctionsDropdown(discord.ui.Select):
    def __init__(self, parent_view: "SetupView"):
        self.parent_view = parent_view

        options = [
            discord.SelectOption(
                label="🌐 Online Notifications",
                value="online",
                description="I'll send a notification each time your MineHut server is online."),

            discord.SelectOption(
                label="🗳️ Vote Notifications",
                value="vote",
                description="I'll send daily notifications where you can vote for MineHut in order to get free credits."),
        ]
        super().__init__(placeholder="Select which bot functions do you want to use ...", min_values=1, max_values=2, options=options)

    async def callback(self, interaction: discord.Interaction):
        config.online_notifications = False
        config.vote_notifications = False

        if "online" in self.values:
            config.online_notifications = True
            config.update_data("settings", "online_notifications", True)
        if "vote" in self.values:
            config.vote_notifications = True
            config.update_data("settings", "vote_notifications", True)

        await self.parent_view.continue_callback(interaction)

class TimezoneDropdown(discord.ui.Select):
    def __init__(self, parent_view: "SetupView"):
        self.parent_view = parent_view

        options = [
            discord.SelectOption(label="UTC / GMT", value="UTC"),
            discord.SelectOption(label="EST (New York / Toronto)", value="America/New_York"),
            discord.SelectOption(label="CST (Chicago / Mexico City)", value="America/Chicago"),
            discord.SelectOption(label="MST (Denver)", value="America/Denver"),
            discord.SelectOption(label="PST (Los Angeles / Vancouver)", value="America/Los_Angeles"),
            discord.SelectOption(label="GMT (London / Dublin)", value="Europe/London"),
            discord.SelectOption(label="CET (Paris / Berlin / Rome)", value="Europe/Paris"),
            discord.SelectOption(label="EET (Athens / Cairo)", value="Europe/Athens"),
            discord.SelectOption(label="MSK (Moscow)", value="Europe/Moscow"),
            discord.SelectOption(label="IST (India)", value="Asia/Kolkata"),
            discord.SelectOption(label="SGT (Singapore)", value="Asia/Singapore"),
            discord.SelectOption(label="JST (Tokyo)", value="Asia/Tokyo"),
            discord.SelectOption(label="AEST (Sydney / Melbourne)", value="Australia/Sydney"),
            discord.SelectOption(label="NZST (Auckland)", value="Pacific/Auckland"),
        ]

        super().__init__(placeholder="Select your server's timezone...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.timezone = self.values[0]
        config.TIMEZONE = self.values[0]
        config.update_data("settings", "timezone", self.values[0])
        await interaction.response.edit_message(view=self.parent_view)

class TimeModal(discord.ui.Modal, title="Timing for vote notifications"):
    vote_time = discord.ui.TextInput(
        label="Set timeing for daily vote notifications:",
        placeholder="e. g. 06:30 pm",
        min_length=7,
        max_length=8,
        required=True
    )

    def __init__(self, parent_view: "SetupView"):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        time_str = self.vote_time.value.strip().lower()

        try:
            converted_time = datetime.strptime(time_str, "%I:%M %p").time()
            self.parent_view.vote_time = converted_time
            config.VOTE_TIME = converted_time
            config.update_data("settings", "vote_time", str(converted_time))

            await interaction.response.edit_message(view=self.parent_view)

        except ValueError:
            return await interaction.response.send_message("❌ **Invalid Format!** Please use the format `HH:MM am/pm` (e.g., `06:30 pm`).", ephemeral=True)

class SetupView(discord.ui.View):
    def __init__(self, cog: "DiscordCog"):
        super().__init__(timeout=None)
        self.cog : cog = cog
        self.current_page : int = 0
        self.staff_role : discord.Role | None = None
        self.notification_channel : discord.TextChannel | None = None
        self.server_name : str | None = None
        self.online_role : discord.Role | None = None
        self.vote_role : discord.Role | None = None
        self.timezone : str | None = None
        self.vote_time : datetime | None = None
        self.create_page()

    def create_page(self):
        self.clear_items()

        # --- Social/Link Buttons ---
        if self.current_page == 0:
            self.add_item(discord.ui.Button(label="YouTube", style=discord.ButtonStyle.link, url="https://www.youtube.com/@EchoDevlog"))
            self.add_item(discord.ui.Button(label="Discord Server", style=discord.ButtonStyle.link, url="https://discord.gg/example"))

        # --- Step 1: Staff Role ---
        elif self.current_page == 1:
            self.add_item(RoleDropdown(parent_view=self, role_type="STAFF_ROLE"))

        # --- Step 2: Channel Selection ---
        elif self.current_page == 2:
            self.add_item(ChannelDropdown(parent_view=self))

        # --- Step 3: Server Name ---
        elif self.current_page == 3:
            modal_btn = discord.ui.Button(label="Press here to enter your server name", style=discord.ButtonStyle.red)
            modal_btn.callback = self.open_name_modal_callback
            self.add_item(modal_btn)

        # --- Step 4: Toggle Functions ---
        elif self.current_page == 4:
            self.add_item(FunctionsDropdown(parent_view=self))

        # --- Step 5: Online Role ---
        elif self.current_page == 5:
            self.add_item(RoleDropdown(parent_view=self, role_type="ONLINE_ROLE"))

        # --- Step 6: Vote Role ---
        elif self.current_page == 6 and config.vote_notifications:
            self.add_item(RoleDropdown(parent_view=self, role_type="VOTE_ROLE"))

        # --- Step 7: Timezone & Timing ---
        elif self.current_page == 7 and config.vote_notifications:
            self.add_item(TimezoneDropdown(parent_view=self))
            time_btn = discord.ui.Button(label="Enter set time here!", style=discord.ButtonStyle.red, row=1)
            time_btn.callback = self.open_time_modal_callback
            self.add_item(time_btn)

        if self.current_page not in [1, 2, 3, 4, 5, 6]:
            next_embed = self.cog.dc_embed_for_setup(self.current_page + 1)

            if next_embed:
                continue_btn = discord.ui.Button(label="Continue", style=discord.ButtonStyle.green, row=4)
                continue_btn.callback = self.continue_callback
                self.add_item(continue_btn)
            else:
                finish_btn = discord.ui.Button(label="Finish Setup", style=discord.ButtonStyle.blurple, row=4)
                finish_btn.callback = self.continue_callback
                self.add_item(finish_btn)

    async def continue_callback(self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer()
        self.current_page += 1

        if self.current_page == 5 and not config.online_notifications:
            self.current_page += 1

        if self.current_page == 6 and not config.vote_notifications:
            self.current_page += 2

        self.create_page()
        next_embed = self.cog.dc_embed_for_setup(self.current_page)

        if next_embed:
            await interaction.edit_original_response(embed=next_embed, view=self)

        else:
            if config.vote_notifications:
                if config.TIMEZONE is None:
                    return await  interaction.followup.send("Please select your timezone before finishing setup.", ephemeral=True)
                elif config.VOTE_TIME is None:
                    return await  interaction.followup.send("Please enter when you'd line to receive vote notifications via red button.", ephemeral=True)

            self.clear_items()

            online_str = f"{config.ONLINE_ROLE.mention}" if config.ONLINE_ROLE else f""
            vote_str = f"{config.VOTE_ROLE.mention}" if config.VOTE_ROLE else f""

            embed = discord.Embed(
                title="✅ Setup complete!",
                description=(
                    f"Staff: {config.STAFF_ROLE.mention}"
                    f"\n\nServer: `{config.SERVER_NAME}`"
                    f"\nOnline Notifications: `{config.online_notifications}`, {online_str}"
                    f"\nVote Notifications: `{config.vote_notifications}`, {vote_str}"
                    f"\n\nTimezone: `{config.TIMEZONE}`"
                    f"\nVote Time: `{self.vote_time.strftime('%I:%M %p') if self.vote_time else 'N/A'}`"
                    f"\n\nThank you for choosing me!"),
                color=discord.Color.green()
            )
            self.add_item(discord.ui.Button(label="YouTube", style=discord.ButtonStyle.link, url="https://www.youtube.com/@EchoDevlog"))
            self.add_item(discord.ui.Button(label="Discord Server", style=discord.ButtonStyle.link, url="https://discord.gg/example"))

            await interaction.edit_original_response(embed=embed, view=self)
            config.setup_completed = True
            config.update_data("settings", "setup_completed", True)
            self.stop()

    async def open_name_modal_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MineHutModal(self))

    async def open_time_modal_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TimeModal(self))


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
                color=discord.Color.orange())

        elif embed_page == 1:
            return discord.Embed(
                title="Step 1: Staff",
                description="Please select which role is your a staff role in the dropdown below:",
                color=discord.Color.orange())

        elif embed_page == 2:
            return discord.Embed(
                title="Step 2: Minecraft Server Updates",
                description="Please select a channel in which I can send notifications about your minecraft server.",
                color=discord.Color.orange())

        elif embed_page == 3:
            return discord.Embed(
                title="Step 3: Name of your MineHut server",
                description="Please enter your MineHut's server name:",
                color=discord.Color.orange())

        elif embed_page == 4:
            return discord.Embed(
                title="Step 4: Bot's functions",
                description="Please select which bot's functions do you want to use. You can select one or both functions.",
                color=discord.Color.orange())

        elif embed_page == 5:
            if config.online_notifications:
                return discord.Embed(
                    title="Step 5: MC server online notification role",
                    description="Which role can bot ping each time your Minecraft server goes online?",
                    color=discord.Color.orange()
                )

        elif config.vote_notifications:
            if embed_page == 6:
                return discord.Embed(
                    title="Step 6: Vote notification role",
                    description="Which role can bot ping for vote notifications?",
                    color=discord.Color.orange()
                )

            elif embed_page == 7:
                return discord.Embed(
                    title="Step 7: Notification Timing",
                    description=
                        ("1. Select your **Timezone**."
                        "\n2. Click the button to set your **preferred time**."
                        "\n3. Press `Finish` button. (If you don't see your selected options but you did select them don't panic. The options were saved."),
                    color=discord.Color.orange())
            else:
                return None

        return None

    @app_commands.command(name="setup", description="Initial set up for the bot")
    @app_commands.guilds(config.GUILD_ID)
    async def dc_setup(self, interaction: discord.Interaction):
        if config.STAFF_ROLE is not None:
            if not any(role == config.STAFF_ROLE for role in interaction.user.roles):
                return await interaction.response.send_message("You don't have permission to use this function!", ephemeral=True)

        if config.setup_completed:
            embed = discord.Embed(
                title="Setup was already completed",
                description=("`/setup` function can only be run once. It seems like you already did that. If you'd like to change any bot's settings you can do it by using commands below:"
                             "\n`/change notification channel`"
                             "\n`/stop online notifications`"
                             "\n`/stop vote notifications`"
                             "\n`/change server name`"
                             "\n`/change time zone`"
                             "\n`/chainge vote timing`"
                             "\n`/change vote role`"
                             "\n`/change online role`"),
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        view = SetupView(self)
        embed = self.dc_embed_for_setup(0)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="data-test", description="Test function for data readability")
    @app_commands.guilds(config.GUILD_ID)
    async def data_test(self, interaction: discord.Interaction):
        output = (
            f"setup_completed: {config.setup_completed}"
            f"\nonline_notifications: {config.online_notifications}"
            f"\nvote_notifications: {config.vote_notifications}"
            f"\nSERVER_NAME: {config.SERVER_NAME}"
            f"\nTIMEZONE: {config.TIMEZONE}"
            f"\nVOTE_TIME: {config.VOTE_TIME}"
            f"\nNOTIFICATIONS_CHANNEL: {config.NOTIFICATIONS_CHANNEL}"
            f"\nSTAFF_ROLE: {config.STAFF_ROLE}"
            f"\nONLINE_ROLE: {config.ONLINE_ROLE}"
            f"\nVOTE_ROLE: {config.VOTE_ROLE}"
            f"\nonline_message: {config.online_message}"
            f"\nvote_message: {config.vote_message}"
        )
        await interaction.response.send_message(output)

async def setup(bot: commands.Bot):
    await bot.add_cog(DiscordCog(bot))