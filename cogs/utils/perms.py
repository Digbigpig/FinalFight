# permissions to check for commands
# We'll attempt to load from the file again as well.
import discord.utils
from discord.ext import commands

from cogs.utils import exceptions
from cogs.utils.classes.weapon.weapons import weapon_dict
from cogs.utils.inserts import create_user
from cogs.utils.querys import server_roles, role_exists, channel_exists, user_exists, user_turn, match_rule, \
    player_data, player_owns_weapon


# Checks permission based on the attribute given.
def check_permissions(ctx, perms):
    msg = ctx.message

    ch = msg.channel
    author = msg.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())


def check_authorized(ch, author):
    authorized = server_roles(ch.server.id)

    for role in author.roles:
        if role.id in authorized:
            return True
    return False


# Checks permission based on the role.
def role_or_permissions(ctx, check, **perms):
    if perms and check_permissions(ctx, perms):
        return True

    ch = ctx.message.channel
    author = ctx.message.author

    if check_authorized(ch, author):
        return True

    role = discord.utils.find(check, author.roles)
    return role is not None


# Checks permission for Moderators
def mod_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(ctx, lambda r: r.name == 'Staff', **perms)

    # Adds to the command import check
    return commands.check(predicate)


def check_integrity(data, needs_to_exist):
    def predicate(ctx):

        if data == "channel":
            exists = channel_exists(ctx.message.channel.id, ctx.message.server.id)

        elif data == "role":
            if not ctx.message.role_mentions:
                raise exceptions.UserInputError
            exists = role_exists(ctx.message.role_mentions[0].id, ctx.message.server.id)

        elif data == "user":
            exists = user_exists(ctx.message.author.id)

            if not exists:
                create_user(ctx.message.author)
                raise exceptions.DataCreated

        else:
            raise discord.InvalidArgument

        #   If the data should be in the DB but it does not.
        if needs_to_exist and not exists:
            raise exceptions.DataDoesNotExists

        #   If the data should not be in the database.
        elif not needs_to_exist and exists:
            raise exceptions.DataCurrentlyExists

        return True

    return commands.check(predicate)


def check_guild_only():
    def predicate(ctx):
        if isinstance(ctx.message.channel, discord.Channel):
            return True
        raise commands.NoPrivateMessage

    return commands.check(predicate)


def check_turn():
    def predicate(ctx):
        if user_turn(ctx.message.author.id, ctx.message.channel.id):
            return True
        raise exceptions.NotUserTurn

    return commands.check(predicate)


def check_rules():
    def predicate(ctx):
        rule = match_rule(ctx.message.channel.id)
        if rule == 'ranked':
            return True

        if rule == 'unranked':
            # TODO: Determine all the allowed weapons for unranked matches.
            return True

        if rule == 'whip':
            if ctx.message.invoked_with in ['whip']:
                return True

        if rule == 'stake':
            return True

        raise exceptions.RuleViolation

    return commands.check(predicate)


def check_ability():
    def predicate(ctx):
        # Do they have the special attack left? Are they frozen?
        data = player_data(ctx.message.channel.id)
        special_needed = weapon_dict[ctx.invoked_with]['stats']['spec_used']

        if special_needed > data['player']['special']:
            raise exceptions.InsufficientSpecial

        wep_type = weapon_dict[ctx.invoked_with]['stats']['type']
        if data['player']['frozen'] and wep_type == 'melee':
            raise exceptions.PlayerFrozen

        # Do they own the weapon?
        if not weapon_dict[ctx.invoked_with.lower()]['standard_weapon']:
            # If they are a monthly subscriber, they can use the weapon.

            main_server = discord.utils.get(ctx.bot.servers, id='376168624983113728')  # TODO: Add this to settings.
            check_member = discord.utils.get(main_server.members, id=ctx.message.author.id)
            check_role = ''

            if ctx.invoked_with.lower() in ['ice', 'blood', 'smoke']:
                check_role = '564478430004117525'

            elif ctx.invoked_with.lower() in ['dh', 'guth', 'karils']:
                check_role = '564480624870686740'

            if check_member:
                for role in check_member.roles:
                    if role.id in ('488176957989715970', check_role):
                        return True

            if not player_owns_weapon(ctx.message.author.id, ctx.invoked_with.lower()):
                raise exceptions.UnownedWeapon

        return True

    return commands.check(predicate)
