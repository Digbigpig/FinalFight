import sys
import traceback

from discord.ext import commands

import settings
from cogs.utils import inserts, exceptions
from cogs.utils import perms


class Common:
    """
    Common commands.
    """

    #   TODO: Move error handlers to handlers.py or something

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="register_channel", pass_context=True)
    @perms.check_guild_only()
    @perms.mod_or_permissions(administrator=True)
    @perms.check_integrity(data="channel", needs_to_exist=False)
    async def register_channel(self, ctx):
        """
        Use this command to allow the bot to use the current channel for hosting fights.
        This is necessary to for bot functionality.
        """

        channel = ctx.message.channel
        server = ctx.message.server
        inserts.create_channel(channel, server)

        await self.bot.say(f"{ctx.message.author.name} has registered {channel.name} as a fighting room.")

    @commands.command(name="unregister_channel", pass_context=True)
    @perms.check_guild_only()
    @perms.mod_or_permissions(administrator=True)
    @perms.check_integrity(data="channel", needs_to_exist=True)
    async def unregister_channel(self, ctx):
        """
        Unregisters the channel, preventing the bot from using the current channel for fights.
        """

        channel = ctx.message.channel
        server = ctx.message.server
        inserts.remove_channel(channel, server)

        await self.bot.say(f"{ctx.message.author.name} has unregistered {channel.name} as a fighting room.")

    @unregister_channel.error
    @register_channel.error
    async def register_channel_handler(self, error, ctx):
        """A local Error Handler for our command register_channel.
        This will only listen for errors in register_channel.
        The global on_command_error will still be invoked after."""

        if isinstance(error, commands.CheckFailure):
            return await self.bot.say(
                f'You must have an authorized Role or be a mod to register channels.\n' +
                f'Mods can use {settings.PREFIX}authorize @Role to give bot management permissions to a Role.')

        if isinstance(error, commands.NoPrivateMessage):
            return await self.bot.say("You cannot use this command in a direct message.")

        if isinstance(error, exceptions.DataCurrentlyExists):
            return await self.bot.say("This channel is already registered. Use the unregister command to remove it.")

        if isinstance(error, exceptions.DataDoesNotExists):
            return await self.bot.say("This channel is not registered. Use the register command to add it.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name='authorize', pass_context=True)
    @perms.check_guild_only()
    @perms.check_integrity(data="role", needs_to_exist=False)
    @perms.mod_or_permissions(administrator=True)
    async def authorize(self, ctx):
        f"""
        Authorize a role manage the bot and its matches. Example: {settings.PREFIX}authorize @Mods
        It is recommended to authorize a role to manage the bot. Owners and administrators are authorized by default.
        """

        roles = ctx.message.role_mentions
        inserts.create_roles(ctx.message.server, roles[0])
        return await self.bot.say(f"Authorized {roles[0].name}.")

    @commands.command(name='unauthorize', pass_context=True)
    @perms.check_guild_only()
    @perms.check_integrity(data="role", needs_to_exist=True)
    @perms.mod_or_permissions()
    async def unauthorize(self, ctx):

        roles = ctx.message.role_mentions
        inserts.remove_roles(ctx.message.server, roles[0])

        return await self.bot.say(f"Unauthorized {roles[0].name}.")

    @authorize.error
    @unauthorize.error
    async def authorize_handler(self, error, ctx):
        """A local Error Handler for our command register_channel.
        This will only listen for errors in register_channel.
        The global on_command_error will still be invoked after."""

        #   TODO: Catch more errors.

        if isinstance(error, commands.CheckFailure):
            return await self.bot.say(
                f'You must have an authorized Role or be a mod to authorize other Roles.\n' +
                f'Mods can use {settings.PREFIX}authorize @Role to give DeathMatch management permissions to a Role.')

        if isinstance(error, commands.UserInputError):
            return await self.bot.say(
                "You need to mention a role to authorize. Some roles might need to allow mentioning.")

        if isinstance(error, commands.NoPrivateMessage):
            return await self.bot.say("You cannot use this command in a direct message.")

        if isinstance(error, exceptions.DataCurrentlyExists):
            return await self.bot.say("This Role is already authorized. Use the unauthorize command to remove it.")

        if isinstance(error, exceptions.DataDoesNotExists):
            return await self.bot.say("This Role is not authorized. Use the authorize command to authorize it.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(Common(bot))
