import pathlib

import discord
from discord import app_commands
from discord.ext import commands

from bex_tools import cycle_random
from goonbot import Goonbot


class Rats(commands.Cog):
    rats = cycle_random(pathlib.Path("rats.txt").read_text().splitlines())
    recently_reported_rats = []

    def __init__(self, bot: Goonbot):
        self.bot = bot
        # To make a "cog specific" context menu command, we gotta do this little song-and-dance
        # of defining the command as a method, then attaching it to the bot. More can be read here:
        # https://github.com/Rapptz/discord.py/issues/7823#issuecomment-1086830458, written by the library author
        self.report_rat_ctx_menu = app_commands.ContextMenu(
            name="Report Rat",
            callback=self.report_broken_rat,
        )
        self.bot.tree.add_command(self.report_rat_ctx_menu)

    @app_commands.command(name="rat", description="Roll a rat 🐀")
    async def rat(self, interaction: discord.Interaction):
        """A goonbot classic, the /rat command sends a random image of a rat from a list, hand curated by community member Ectoplax"""
        next_rat = next(self.rats)
        await interaction.response.send_message(
            embed=self.bot.embed(title="Rat").set_image(url=next_rat),
        )

    async def report_broken_rat(self, interaction: discord.Interaction, message: discord.Message):
        """
        For whatever reason, links break. This offers a way for users to report images that no longer load in discord embeds

        I'm choosing this over attaching a view to rat message because I find the buttons to be spammy.
        This is a design choice. Buttons take up more vertical real estate than a message without buttons, so only use when necessary
        """
        # Because any message could be reported, we need to validate we're processing a "rat message" before continuing
        # We use short-circuiting to first make sure the message has an embed, THEN check if the embed's title is "rat"
        # If either is not true, return early and abort
        if not message.embeds or message.embeds[0].title != "Rat":
            return await interaction.response.send_message(
                embed=self.bot.embed(title="This isn't a rat post."), ephemeral=True
            )

        # Get the link to the broken rat
        rat_embed = message.embeds[0]
        offending_rat_link = rat_embed.image.url

        # Make sure its not been reported since last restart
        if offending_rat_link in self.recently_reported_rats:
            return await interaction.response.send_message(
                embed=self.bot.embed(
                    title="This rat was recently reported, thank you though!",
                    description="*you flippin' narc..* 📸",
                )
            )

        # Add rat to recent offenders list
        self.recently_reported_rats.append(offending_rat_link)

        # Send message to alert channel (handle report)
        goonbot_alert_channel = self.bot.get_channel(1171291004175912980)
        assert isinstance(goonbot_alert_channel, discord.TextChannel)
        await goonbot_alert_channel.send(
            embed=self.bot.embed(
                title="Rat report",
                description=offending_rat_link,
            ),
        )

        # Give user response
        await interaction.response.send_message(
            embed=self.bot.embed(
                title="Thanks for the report!",
                description="We'll take him out back.. 😵",
            ),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Rats(bot))
