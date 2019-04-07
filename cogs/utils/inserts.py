import random

from sqlalchemy.sql import func

from cogs.utils.models.base import Session
from cogs.utils.models.channel import Channel
from cogs.utils.models.hiscores_report import HiscoresReport
from cogs.utils.models.item import Item
from cogs.utils.models.item_inventory import ItemInventory
from cogs.utils.models.match import Match
from cogs.utils.models.player import Player
from cogs.utils.models.role import Role
from cogs.utils.models.server import Server
from cogs.utils.models.user import User


def create_channel(channel, server):
    session = Session()
    s = session.query(Server).filter(Server.id == server.id).first()
    chan = Channel(channel.id, channel.name, s)
    match = Match(chan)
    p1 = Player(match, 1)
    p2 = Player(match, 2)
    session.add(chan)
    session.add(match)
    session.add(p1)
    session.add(p2)
    session.commit()
    session.close()


def remove_channel(channel, server):
    session = Session()
    chan = session.query(Channel).filter(Channel.id == channel.id and Channel.server_id == server.id).first()
    session.delete(chan)
    session.commit()
    session.close()


def create_server(server_id, server_name):
    session = Session()
    s = Server(server_id, server_name)
    session.add(s)
    session.commit()
    session.close()


def create_roles(serv, role):
    session = Session()
    s = session.query(Server).filter(Server.id == serv.id).first()
    r = Role(role.id, role.name, s)
    session.add(r)
    session.commit()
    session.close()


def remove_roles(serv, role):
    session = Session()
    r = session.query(Role).filter(Role.id == role.id and Role.server_id == serv.id).first()
    session.delete(r)
    session.commit()
    session.close()


def create_user(user):
    session = Session()
    u = User(user.id, user.name)
    session.add(u)
    session.commit()
    session.close()


def add_player_to_match(channel_id, user_id, position, rule, stake=0):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    u = session.query(User).filter(User.id == user_id).first()
    p = session.query(Player).filter(Player.match_id == m.id).filter(Player.position == position).first()
    p.user_id = user_id

    m.stake = stake
    u.gp -= stake

    if rule:
        m.rules = rule

    session.commit()
    session.close()


def begin_match(channel_id):
    #   Match: Set the begin and last play time. Randomize the turn between 1,2
    #   Players: Reset the stats

    session = Session()

    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    m.start_time = func.now()
    m.last_play = func.now()
    m.turn = random.choice([1, 2])

    players = session.query(Player).filter(Player.match_id == m.id).all()

    for player in players:
        player.hp = 99
        player.special = 100
        player.prayer_points = 99
        player.food = 3
        player.poison = False
        player.frozen = False
        player.prayer = None

    session.commit()
    session.close()


def clear_match(channel_id, winner=False):
    # If there is no winner, return the staked amount back to each player
    # If there is a winner add double the staked amount to the winner.
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    players = session.query(Player).filter(Player.match_id == m.id).all()

    if m.rules == "stake" and not winner:
        for player in players:
            if player.user_id:
                player.user.gp += m.stake

    for player in players:
        player.user_id = None

    m.stake = 0
    session.commit()
    session.close()


def poison(channel_id, player_id, poisoned):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    player = session.query(Player).filter(Player.match_id == m.id).filter(Player.user_id == player_id).first()
    player.poison = poisoned
    session.commit()
    session.close()


def frozen(channel_id, player_id, freeze):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    player = session.query(Player).filter(Player.match_id == m.id).filter(Player.user_id == player_id).first()
    player.frozen = freeze
    session.commit()
    session.close()


def damage(channel_id, player_id, dmg):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    player = session.query(Player).filter(Player.match_id == m.id).filter(Player.user_id == player_id).first()
    player.hp -= dmg
    session.commit()
    session.close()


def update_attacker(channel_id, player_id, special, heal):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    player = session.query(Player).filter(Player.match_id == m.id).filter(Player.user_id == player_id).first()
    player.special -= special
    player.hp += heal
    session.commit()
    session.close()


def next_turn(channel_id):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    m.turn += 1
    m.last_play = func.now()
    session.commit()
    session.close()


def create_item(name, description, price):
    session = Session()
    i = Item(name, description, price)
    session.add(i)
    session.commit()
    session.close()


def gain_experience(user_id, exp):
    session = Session()
    u = session.query(User).filter(User.id == user_id).first()
    u.experience += exp
    session.commit()
    session.close()


def gain_gp(user_id, gp):
    session = Session()
    u = session.query(User).filter(User.id == user_id).first()
    u.gp += gp
    session.commit()
    session.close()


def win_lose_history(winner_id, loser_id, server_id):
    session = Session()

    h = session.query(HiscoresReport).filter(HiscoresReport.winner_id == winner_id) \
        .filter(HiscoresReport.loser_id == loser_id) \
        .filter(HiscoresReport.server_id == server_id)

    if h.count() > 0:
        h.first().count += 1
    else:
        r = HiscoresReport(winner_id, loser_id, server_id)
        r.count = 1
        session.add(r)

    session.commit()
    session.close()


def give_item(user_id, item_id):
    session = Session()
    i = session.query(Item).filter(Item.id == item_id).first()
    w = session.query(ItemInventory).filter(ItemInventory.user_id == user_id).filter(ItemInventory.item_id == i.id)

    if w.count() > 0:
        w.first().count += 1

    else:
        n = ItemInventory(user_id, item_id, 1)
        session.add(n)

    session.commit()
    session.close()


def spend_gp(user_id, gp):
    session = Session()
    u = session.query(User).filter(User.id == user_id).first()
    u.gp -= gp
    session.commit()
    session.close()
