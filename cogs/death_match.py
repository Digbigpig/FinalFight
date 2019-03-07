from discord.ext import commands
from discord.utils import get
from cogs.utils import perms, inserts, querys, exceptions
from cogs.utils.classes.weapon.weapons import weapon_dict
import traceback, sys, settings, random, discord

match_rules = ["unranked", "whip", "ranked"]
weapon_check = weapon_dict.keys()
#   TODO: Fix the help command.


class DeathMatch:
    """
    Handles all the game logic for death match
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="attack", pass_context=True, aliases=weapon_check)
    @perms.check_guild_only()
    @perms.check_integrity(data="channel", needs_to_exist=True, )
    @perms.check_integrity(data="user", needs_to_exist=True, )
    @perms.check_turn()     # Is it their turn?
    @perms.check_rules()    # Do the rules allow this weapon?
    @perms.check_ability()  # Do they have the special attack left? Are they frozen?  TODO: Do they own the weapon?
    async def attack(self, ctx):
        match_data = querys.match_data(ctx.message.channel.id)
        poison_damage = 0

        # Create the weapon and generate the damage
        weapon = weapon_dict[ctx.invoked_with]['weapon'](weapon_dict[ctx.invoked_with]['stats'])

        # Will poison be applied?
        if weapon.poison:
            roll = random.randint(1, 3)
            if roll == 1:
                inserts.poison(ctx.message.channel.id,
                               match_data['player'][match_data['match']['defender']]['id'],
                               True)
                match_data['player'][match_data['match']['defender']]['poison'] = True

        # If the enemy is not frozen, will they be frozen?
        if not match_data['player'][match_data['match']['defender']]['frozen'] and weapon.freeze:
            roll = random.randint(1, 3)
            if roll == 1:
                inserts.frozen(ctx.message.channel.id,
                               match_data['player'][match_data['match']['defender']]['id'],
                               True)
                match_data['player'][match_data['match']['defender']]['frozen'] = True

        # If the attacker is frozen will they become unfrozen?
        if match_data['player'][match_data['match']['attacker']]['frozen']:
            roll = random.randint(1, 3)
            if roll == 1:
                inserts.frozen(ctx.message.channel.id,
                               match_data['player'][match_data['match']['attacker']]['id'],
                               False)
                match_data['player'][match_data['match']['attacker']]['frozen'] = False

        # Will the enemy take poison damage?
        if match_data['player'][match_data['match']['defender']]['poison']:
            roll = random.randint(1, 5)
            if roll == 1:
                poison_damage = 6

        # Apply the damage to the enemy.
        inserts.damage(ctx.message.channel.id,
                       match_data['player'][match_data['match']['defender']]['id'],
                       (sum(weapon.damage) + poison_damage))

        # Reduce the attackers spec, apply any healing if weapon.heal
        inserts.update_attacker(ctx.message.channel.id,
                                match_data['player'][match_data['match']['attacker']]['id'],
                                weapon.spec_used,
                                weapon.heal)
        match_data['player'][match_data['match']['attacker']]['special'] -= weapon.spec_used
        match_data['player'][match_data['match']['attacker']]['hp'] += weapon.heal

        # Change the turn.
        inserts.next_turn(ctx.message.channel.id)

        # Is there a winner? Yes --> Remove users from players
        if (sum(weapon.damage) + poison_damage) >= match_data['player'][match_data['match']['defender']]['hp']:
            match_data = querys.match_data(ctx.message.channel.id)
            inserts.clear_match(ctx.message.channel.id)
            return await self.output(match_data, weapon, True)

        # Output() the message.
        return await self.output(match_data, weapon, poison_damage, False)

    async def output(self, match, weapon, poison_damage, won):
        if won:
            return await self.bot.say(f"{match['player'][match['match']['attacker']]['name']}")
        else:
            return await self.bot.say(f"{match['player'][match['match']['attacker']]['name']} did {weapon.damage} weapon damage and {poison_damage} poison damage.\n"
                                      f"{match['player'][match['match']['defender']]['name']} poison {match['player'][match['match']['defender']]['poison']}")

    @attack.error
    async def attack_handler(self, error, ctx):

        if isinstance(error, commands.NoPrivateMessage):
            return await self.bot.say("You cannot use this command in a direct message.")

        if isinstance(error, exceptions.DataCreated):
            return await self.bot.say(
                "Thank you for playing Deathmatch! \n"
                "Since this is your first time playing, I have created a profile for you.\n"
                f"You can now use the {ctx.invoked_with} command.")

        if isinstance(error, exceptions.DataDoesNotExists):
            return await self.bot.say("This channel is not registered. Use the register command to add it.")

        if isinstance(error, exceptions.NotUserTurn):
            return await self.bot.say("It is not your turn.")

        if isinstance(error, exceptions.RuleViolation):
            return await self.bot.say("It is against the match rules to use that weapon!")

        if isinstance(error, exceptions.InsufficientSpecial):
            return await self.bot.say("You do not have enough special attack left!")

        if isinstance(error, exceptions.PlayerFrozen):
            return await self.bot.say("You are frozen and must used a ranged or magic attack.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name="test_embed", pass_context=True)
    async def test_embed(self, ctx):
        hp_left = get(ctx.message.server.emojis, name="HPGREENLEFT")
        hp_mid = get(ctx.message.server.emojis, name="HPGREENMID")
        hp_right = get(ctx.message.server.emojis, name="HPGREENRIGHT")

        embed = discord.Embed(title="Digbigpig Whipped Broken", description="Broken took 45 damage!", type='rich', color=0x00ff00)
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.add_field(name='Broken', value='\u200b', inline=False)
        embed.add_field(name='HP', value='99 ░░░░░░░░░░░░░░░░░░░░', inline=True)
        embed.add_field(name='SpecialAttack', value='100', inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=False)
        embed.add_field(name='Digbigpig', value='\u200b', inline=False)
        embed.add_field(name='HP', value=f'99 {hp_left}{hp_mid}{hp_mid}{hp_mid}{hp_mid}{hp_mid}{hp_mid}{hp_right}', inline=True)
        embed.add_field(name='Special', value='100', inline=True)

        await self.bot.say(f"`Digbigpig dealt 45 damage to Broken.` ")
        await self.bot.say(f"`Broken dealt 2, 14, 29, 3 damage to Digbigpig.`")

        return await self.bot.say(embed=embed)

    @commands.command(name="dm", pass_context=True)
    @perms.check_guild_only()
    @perms.check_integrity(data="channel", needs_to_exist=True,)
    @perms.check_integrity(data="user", needs_to_exist=True,)
    async def dm(self, ctx):
        p_count = querys.get_player_count(ctx.message.channel.id)

        try:
            rule = ctx.message.content.split()[1].lower()
        except IndexError:
            rule = "ranked"

        if rule not in match_rules and p_count == 0:
            return await self.bot.say(f"{rule} is not a valid match type.\n Match rules: {str(match_rules)}")

        if p_count == 0:
            #   Get the match rule and add that player as player 1.
            inserts.add_player_to_match(ctx.message.channel.id, ctx.message.author.id, 1, rule)
            return await self.bot.say(f"{ctx.message.author.name} has requested a {rule.upper()} fight!\n"
                                      f"Type {settings.PREFIX}dm to accept!")

        elif p_count == 1:
            #   add that player as player 2, initialize the match and player settings. the match can start

            if not querys.player_in_match(ctx.message.author.id, ctx.message.channel.id):
                inserts.add_player_to_match(ctx.message.channel.id, ctx.message.author.id, 2)
                inserts.begin_match(ctx.message.channel.id)
                data = querys.match_data(ctx.message.channel.id)

                return await self.bot.say(f"{data['player']['2']['name']} has accepted "
                                          f"{data['player']['1']['name']}'s fight.\n"
                                          f"It is "
                                          f"{['', data['player']['1']['name'], data['player']['2']['name']][data['match']['turn']]}'s turn first")

            else:
                return await self.bot.say("You cannot accept your own fight.")

        else:
            return await self.bot.say(f"Please wait for the current match to end before starting another.")

    @commands.command(name="clear_match", pass_context=True)
    @perms.check_guild_only()
    @perms.mod_or_permissions()
    @perms.check_integrity(data="channel", needs_to_exist=True, )
    async def clear_match(self, ctx):
        inserts.clear_match(ctx.message.channel.id)

        return await self.bot.say(f"The match has been force reset by {ctx.message.author.name}")

    @dm.error
    @clear_match.error
    async def dm_handler(self, error, ctx):
        """A local Error Handler for our command register_channel.
        This will only listen for errors in register_channel.
        The global on_command_error will still be invoked after."""

        if isinstance(error, commands.CheckFailure):
            return await self.bot.say(
                f'You must have an authorized Role or be a mod to use this command.\n' +
                f'Mods can use {settings.PREFIX}authorize @Role to give bot management permissions to a Role.')

        if isinstance(error, commands.NoPrivateMessage):
            return await self.bot.say("You cannot use this command in a direct message.")

        if isinstance(error, exceptions.DataCreated):
            return await self.bot.say(
                "Thank you for playing Deathmatch! \n"
                "Since this is your first time playing, I have created a profile for you.\n"
                f"You can now use the {ctx.invoked_with} command.")

        if isinstance(error, exceptions.DataDoesNotExists):
            return await self.bot.say("This channel is not registered. Use the register command to add it.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(DeathMatch(bot))
