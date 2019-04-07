import discord
import random
import settings
import sys
import traceback

from discord.ext import commands
from discord.utils import get

from cogs.utils import perms, inserts, querys, exceptions
from cogs.utils.classes.weapon.weapons import weapon_dict

match_rules = ["unranked", "whip", "ranked", "stake"]
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
        if ctx.invoked_with == 'attack':
            return await self.bot.say(f"Define a weapon to attack with. Use {settings.PREFIX}weapons fora detailed list of weapons to use")

        match_data = querys.match_data(ctx.message.channel.id)
        poisoned = None
        frozen = None
        poison_damage = 0

        # Create the weapon and generate the damage
        weapon = weapon_dict[ctx.invoked_with]['weapon'](weapon_dict[ctx.invoked_with]['stats'],
                                                         match_data)

        # Will poison be applied?
        if weapon.poison:
            roll = random.randint(1, 3)
            if roll == 1:
                inserts.poison(ctx.message.channel.id,
                               match_data['player'][match_data['match']['defender']]['id'],
                               True)
                match_data['player'][match_data['match']['defender']]['poison'] = True
                poisoned = True

        # If the enemy is not frozen, will they be frozen?
        if not match_data['player'][match_data['match']['defender']]['frozen'] and weapon.freeze:
            roll = random.randint(1, 3)
            if roll == 1:
                inserts.frozen(ctx.message.channel.id,
                               match_data['player'][match_data['match']['defender']]['id'],
                               True)
                match_data['player'][match_data['match']['defender']]['frozen'] = True
                frozen = True

        # If the attacker is frozen will they become unfrozen?
        if match_data['player'][match_data['match']['attacker']]['frozen']:
            roll = random.randint(1, 3)
            if roll == 1:
                inserts.frozen(ctx.message.channel.id,
                               match_data['player'][match_data['match']['attacker']]['id'],
                               False)
                match_data['player'][match_data['match']['attacker']]['frozen'] = False
                frozen = False

        # Will the enemy take poison damage?
        if match_data['player'][match_data['match']['defender']]['poison']:
            roll = random.randint(1, 5)
            if roll == 1:
                poison_damage = 6

        # Apply the damage to the enemy.
        inserts.damage(ctx.message.channel.id,
                       match_data['player'][match_data['match']['defender']]['id'],
                       (sum(weapon.damage) + poison_damage))
        match_data['player'][match_data['match']['defender']]['hp'] -= sum(weapon.damage, poison_damage)

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
        if match_data['player'][match_data['match']['defender']]['hp'] <= 0:
            xp = 100 + int(match_data['player'][match_data['match']['attacker']]['hp'])
            gp = random.randint(1000, 5000)
            stake = querys.get_stake(ctx.message.channel.id) * 2

            inserts.gain_experience(ctx.message.author.id, xp)
            inserts.gain_gp(ctx.message.author.id, (gp + stake))
            inserts.win_lose_history(match_data['player'][match_data['match']['attacker']]['id'],
                                     match_data['player'][match_data['match']['defender']]['id'],
                                     ctx.message.server.id)
            inserts.clear_match(ctx.message.channel.id, winner=True)

            return await self.output(ctx, match_data, weapon, frozen, poisoned, poison_damage, won=True, gp=gp, xp=xp, stake=stake)

        # Output() the message.
        return await self.output(ctx, match_data, weapon, frozen, poisoned, poison_damage, won=False)

    async def output(self, ctx, match, weapon, frozen, poisoned, poison_damage, won, **kwargs):

        # How much damage was dealt with the weapon.
        embed = discord.Embed(
            title=f"{match['player'][match['match']['attacker']]['name']} used {ctx.invoked_with.upper()}!",
            description=f"{match['player'][match['match']['defender']]['name']} took {str(weapon.damage)} damage!",
            type='rich', color=0x00ff00)
        embed.set_thumbnail(url=ctx.message.author.avatar_url)

        # Healed
        if weapon.heal:
            embed.add_field(name=f"{match['player'][match['match']['attacker']]['name']} has been healed {weapon.heal} HP.",
                            value=":heart:",
                            inline=False)

        # Poisoned
        if poisoned:
            embed.add_field(name=f"{match['player'][match['match']['defender']]['name']} has been POISONED.",
                            value=":green_heart:",
                            inline=False)

        # Extra damage: Poison
        if poison_damage:
            embed.add_field(name=f"{match['player'][match['match']['defender']]['name']} took {poison_damage} damage from poison.",
                            value=":green_heart:",
                            inline=False)
        # Were they frozen
        if frozen:
            embed.add_field(name=f"{match['player'][match['match']['defender']]['name']} was FROZEN.",
                            value=f":blue_heart:",
                            inline=False)

        # Add the health bars and stats
        bar = self.gen_hpbar(ctx, match['player']['1']['hp'])
        embed.add_field(name='\u200b', value='\u200b', inline=False)
        embed.add_field(name=f"{match['player']['1']['name']}",
                        value=f'{bar[0]}{bar[1]}{bar[2]}{bar[3]}{bar[4]}{bar[5]}{bar[6]}{bar[7]}{bar[8]}{bar[9]}',
                        inline=False)
        embed.add_field(name=f'HP',
                        value=f"{str(match['player']['1']['hp'])}",
                        inline=True)
        embed.add_field(name='Special', value=f"{match['player']['1']['special']}", inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=False)

        bar = self.gen_hpbar(ctx, match['player']['2']['hp'])
        embed.add_field(name=f"{match['player']['2']['name']}",
                        value=f'{bar[0]}{bar[1]}{bar[2]}{bar[3]}{bar[4]}{bar[5]}{bar[6]}{bar[7]}{bar[8]}{bar[9]}',
                        inline=False)
        embed.add_field(name='HP',
                        value=f"{str(match['player']['2']['hp'])}",
                        inline=True)

        embed.add_field(name='Special', value=f"{match['player']['2']['special']}", inline=True)

        # Did someone win
        if won:
            wins = querys.get_server_wins(match['player'][match['match']['attacker']]['id'],
                                          ctx.message.server.id)
            embed.add_field(name='\u200b', value='\u200b', inline=False)
            embed.add_field(name=f"{match['player'][match['match']['attacker']]['name']} has WON!",
                            value=f"{match['player'][match['match']['attacker']]['name']} gained "
                            f"{kwargs['xp']} XP and {kwargs['gp']} GP {str(kwargs['stake']) + ' stake winnings.' if kwargs['stake'] else ''}",
                            inline=False)
            embed.add_field(name=f"{match['player'][match['match']['attacker']]['name']} now has {wins} wins in this server!",
                            value=f":pig:",
                            inline=False)

        return await self.bot.say(embed=embed)

    def gen_hpbar(self, ctx, thp):
        bar = []
        hp = int(thp)
        if hp > 99:
            hp = 99
        if hp < 0:
            hp = 0

        # Create the left cap.
        if hp >= 10:
            bar.append(get(self.bot.get_server(settings.emoji_server).emojis, name=settings.emojis['left'][4]))
        else:
            left = int((hp % 10) / 2)
            bar.append(get(self.bot.get_server(settings.emoji_server).emojis, name=settings.emojis['left'][left]))

        # Create the middle bars.
        for i in range(2, 10):
            if hp >= (10 * i):
                bar.append(get(self.bot.get_server(settings.emoji_server).emojis, name=settings.emojis['mid'][0]))
            else:
                dif = (i * 10) - hp
                if dif >= 10:
                    bar.append(get(self.bot.get_server(settings.emoji_server).emojis, name=settings.emojis['mid'][5]))
                else:
                    left = int((dif % 10) / 2)
                    bar.append(get(self.bot.get_server(settings.emoji_server).emojis, name=settings.emojis['mid'][left]))

        # Create the right cap.
        dif = 99 - hp
        if dif >= 9:
            bar.append(get(self.bot.get_server(settings.emoji_server).emojis, name=settings.emojis['right'][4]))
        else:
            left = int((dif % 10) / 2)
            bar.append(get(self.bot.get_server(settings.emoji_server).emojis, name=settings.emojis['right'][left]))

        return bar

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

        if isinstance(error, exceptions.UnownedWeapon):
            return await self.bot.say(f"You have not unlocked this weapon yet! Use {settings.PREFIX}store to purchase weapons.")

        if isinstance(error, exceptions.InsufficientSpecial):
            return await self.bot.say("You do not have enough special attack left!")

        if isinstance(error, exceptions.PlayerFrozen):
            return await self.bot.say("You are frozen and must used a ranged or magic attack.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # @app.route('/')
    # def test_route():
    #     print("testing")
    #     bot.send_message(destination=discord.Object(id=settings.BROADCAST_ID),
    #                      content=f"Testing")
    #     return "Testing "

    @commands.command(name="dm", pass_context=True)
    @perms.check_guild_only()
    @perms.check_integrity(data="channel", needs_to_exist=True,)
    @perms.check_integrity(data="user", needs_to_exist=True,)
    async def dm(self, ctx):
        p_count = querys.get_player_count(ctx.message.channel.id)
        stake = 0

        try:
            rule = ctx.message.content.split()[1].lower()
        except IndexError:
            rule = "ranked"

        if rule == 'stake' and p_count == 0:
            try:
                stake = int(ctx.message.content.split()[-1])
                if stake < 0:
                    raise ValueError
            except ValueError:
                return await self.bot.say(f"You must define a positive amount to stake. Example Usage: {settings.PREFIX}dm stake 5000")

        if rule not in match_rules and p_count == 0:
            return await self.bot.say(f"{rule} is not a valid match type.\n Match rules: {str(match_rules)}")

        if p_count == 0:
            #   Get the match rule and add that player as player 1.
            # If it is a staked match, check that they have have enough gp to stake
            # Add the stake amount to the match
            # Remove the stake amount from their gp
            if rule == 'stake':
                if not querys.user_has_enough_gp(ctx.message.author.id, stake):
                    return await self.bot.say("You do not have enough gp to stake that much")

            inserts.add_player_to_match(ctx.message.channel.id, ctx.message.author.id, 1, rule, stake=stake)
            return await self.bot.say(f"**{ctx.message.author.name} (Lvl - {querys.get_rank(ctx.message.author.id)})** "
                                      f"has requested a {rule.upper()}{' of ' + str(stake) if stake else '' } fight!\n"
                                      f"Type {settings.PREFIX}dm to accept!")

        elif p_count == 1:
            #   add that player as player 2, initialize the match and player settings. the match can start
            if not querys.player_in_match(ctx.message.author.id, ctx.message.channel.id):
                # Get the match rule
                # If it is a staked match, ensure hey have enough gp to stake

                rule = querys.match_rule(ctx.message.channel.id)

                if rule == 'stake':
                    stake = querys.get_stake(ctx.message.channel.id)
                    if not querys.user_has_enough_gp(ctx.message.author.id, stake):
                        return await self.bot.say("You do not have enough gp to stake that much")

                inserts.add_player_to_match(ctx.message.channel.id, ctx.message.author.id, 2, rule=rule, stake=stake)
                inserts.begin_match(ctx.message.channel.id)
                data = querys.match_data(ctx.message.channel.id)

                return await self.bot.say(f"**{data['player']['2']['name']} (Lvl - {querys.get_rank(ctx.message.author.id)})** has accepted "
                                          f"**{data['player']['1']['name']} (Lvl - {querys.get_rank(data['player']['1']['id'])})**'s fight.\n"
                                          f"It is "
                                          f"{['', data['player']['1']['name'], data['player']['2']['name']][data['match']['turn']]}'s turn first")

            else:
                return await self.bot.say("You cannot accept your own fight.")

        else:
            return await self.bot.say(f"Please wait for the current match to end before starting another.")

    @commands.command(name="clear_match", pass_context=True)
    @perms.check_guild_only()
    @perms.mod_or_permissions(administrator=True)
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

    @commands.command(name="store", pass_context=True)
    @perms.check_integrity(data="user", needs_to_exist=True, )
    async def store(self, ctx):
        items = querys.get_items()
        try:
            item = ctx.message.content.split()[1]

        except IndexError:

            embed = discord.Embed(title="Welcome to the Death Match store!",
                                  description=f"Here you can unlock the most powerful weapons."
                                  f" Type {settings.PREFIX}store [ItemName] here to unlock it",
                                  type='rich',
                                  color=0x00ff00)
            for i in items:
                embed.add_field(name=f"{i['name']} - {i['cost']} GP",
                                value=f"{i['description']}")
            return await self.bot.say(embed=embed)

        for i in items:
            if i['name'] == item:
                if querys.user_has_enough_gp(ctx.message.author.id, i['cost']):
                    inserts.give_item(ctx.message.author.id, i['id'])
                    inserts.spend_gp(ctx.message.author.id, i['cost'])
                    return await self.bot.say(f"Congrats {ctx.message.author.name}! You have unlocked the {i['name']} weapon!")
                return await self.bot.say(f"You do not haven enough gp to purchase that! "
                                          f"Type {settings.PREFIX}inventory to see how much gp and what itmes you currently own.")
        return await self.bot.say(f"I could not find that item. Type {settings.PREFIX}store to see all purchasable items.")

    @store.error
    async def store_handler(self, error, ctx):

        if isinstance(error, exceptions.DataCreated):
            return await self.bot.say(
                "Thank you for playing Deathmatch! \n"
                "Since this is your first time playing, I have created a profile for you.\n"
                f"You can now use the {ctx.invoked_with} command.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name="inventory", pass_context=True)
    @perms.check_integrity(data="user", needs_to_exist=True, )
    async def inventory(self, ctx):
        gp = querys.get_user_gp(ctx.message.author.id)
        user_inventory = querys.get_user_inventory(ctx.message.author.id)

        embed = discord.Embed(title=f"{ctx.message.author.name}'s Inventory",
                              description=f"GP: {gp}",
                              type='rich',
                              color=0x00ff00)
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        for i in user_inventory:
            embed.add_field(name=f"{i['name']}",
                            value=f"X {i['count']}")

        return await self.bot.say(embed=embed)

    @inventory.error
    async def inventory_handler(self, error, ctx):

        if isinstance(error, exceptions.DataCreated):
            return await self.bot.say(
                "Thank you for playing Deathmatch! \n"
                "Since this is your first time playing, I have created a profile for you.\n"
                f"You can now use the {ctx.invoked_with} command.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name="hiscores", pass_context=True)
    @perms.check_integrity(data="user", needs_to_exist=True, )
    @perms.check_guild_only()
    async def hiscores(self, ctx):
        if 'local' in ctx.message.content:
            scope = 'Server'
            scores = querys.get_server_hiscores(ctx.message.server.id)
        else:
            scope = 'Global'
            scores = querys.get_global_hiscores()

        embed = discord.Embed(title=f"{scope} Hiscores",
                              description=f":crossed_swords: Top players by wins",
                              type='rich',
                              color=0x00ff00)
        embed.set_thumbnail(url=ctx.message.server.icon_url)
        for i in scores:
            embed.add_field(name=f"{i[1]}",
                            value=f"{i[2]}",
                            inline=False)

        return await self.bot.say(embed=embed)

    @hiscores.error
    async def hiscores_handler(self, error, ctx):

        if isinstance(error, exceptions.DataCreated):
            return await self.bot.say(
                "Thank you for playing Deathmatch! \n"
                "Since this is your first time playing, I have created a profile for you.\n"
                f"You can now use the {ctx.invoked_with} command.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name="weapons", pass_context=True)
    @perms.check_integrity(data="user", needs_to_exist=True, )
    async def weapons(self, ctx):
        embed = discord.Embed(title=f"Weapons",
                              description=f":crossed_swords:",
                              type='rich',
                              color=0x00ff00)
        embed.set_thumbnail(url=ctx.message.server.icon_url)

        for weapon in weapon_dict:
            embed.add_field(name=f"{weapon}",
                            value=f"||Max Hit: {weapon_dict[weapon]['stats']['max_hit']} X {weapon_dict[weapon]['stats']['times_hit']} "
                            f"Special attack needed: {weapon_dict[weapon]['stats']['spec_used']}||",
                            inline=True)
        return await self.bot.say(embed=embed)

    @weapons.error
    async def weapons_handler(self, error, ctx):

        if isinstance(error, exceptions.DataCreated):
            return await self.bot.say(
                "Thank you for playing Deathmatch! \n"
                "Since this is your first time playing, I have created a profile for you.\n"
                f"You can now use the {ctx.invoked_with} command.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(DeathMatch(bot))
