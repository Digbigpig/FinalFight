from sqlalchemy.sql import exists, func, text

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


def servers():
    session = Session()
    s = session.query(Server).all()
    session.close()
    return s


def server(server_id):
    session = Session()
    s = session.query(Server).filter(Server.id == server_id).first()
    session.close()
    return s


def server_exists(server_id):
    session = Session()
    s = session.query(exists().where(Server.id == server_id)).scalar()
    session.close()
    return s


def channel_exists(channel_id, server_id):
    session = Session()
    s = session.query(exists().where(Channel.id == channel_id and Channel.server_id == server_id)).scalar()
    session.close()
    return s


def server_roles(server_id):
    session = Session()
    s = session.query(Server).filter(Server.id == server_id).first()
    results = [str(role.id) for role in s.roles]
    session.close()
    return results


def role_exists(role_id, server_id):
    session = Session()
    s = session.query(exists().where(Role.id == role_id and Role.server_id == server_id)).scalar()
    session.close()
    return s


def user_exists(user_id):
    session = Session()
    s = session.query(exists().where(User.id == user_id)).scalar()
    session.close()
    return s


def get_player_count(channel_id):
    count = 0
    session = Session()
    m = session.query(Player).join(Match).filter(Match.channel_id == channel_id).all()
    for p in m:
        if p.user_id is not None:
            count += 1
    session.close()
    return count


def player_in_match(user_id, channel_id):
    result = False
    session = Session()
    m = session.query(Player).join(Match).filter(Match.channel_id == channel_id).all()
    for p in m:
        if p.user_id == user_id:
            result = True
    session.close()
    return result


def match_data(channel_id):
    data = {}
    session = Session()

    m = session.query(Match).filter(Match.channel_id == channel_id).first()

    if m.turn % 2 == 0:  # Even turns are player 2, odd is player 1
        attacker = 2
        defender = 1
    else:
        attacker = 1
        defender = 2

    data['match'] = {'turn': m.turn, 'rules': m.rules, 'attacker': str(attacker), 'defender': str(defender)}

    players = session.query(Player).filter(Player.match_id == m.id).all()

    data['player'] = {}
    for player in players:
        data['player'][str(player.position)] = {'id': player.user_id,
                                                'name': player.user.name,
                                                'hp': player.hp,
                                                'special': player.special,
                                                'prayer_points': player.prayer_points,
                                                'food': player.food,
                                                'frozen': player.frozen,
                                                'poison': player.poison,
                                                'prayer': player.prayer, }
    session.commit()
    session.close()
    return data


def user_turn(user_id, channel_id):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()

    if m.turn % 2 == 0:  # Even turns are player 2, odd is player 1
        turn = 2
    else:
        turn = 1

    s = session.query(exists()
                      .where(Player.match_id == m.id)
                      .where(Player.position == turn)
                      .where(Player.user_id == user_id)).scalar()
    session.close()
    return s


def match_rule(channel_id):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    r = m.rules
    session.close()
    return r


def player_data(channel_id):
    data = {}
    session = Session()

    m = session.query(Match).filter(Match.channel_id == channel_id).first()

    if m.turn % 2 == 0:  # Even turns are player 2, odd is player 1
        turn = 2
    else:
        turn = 1

    player = session.query(Player).filter(Player.match_id == m.id).filter(Player.position == turn).first()
    data['player'] = {'name': player.user.name,
                      'hp': player.hp,
                      'special': player.special,
                      'prayer_points': player.prayer_points,
                      'food': player.food,
                      'frozen': player.frozen,
                      'poison': player.poison,
                      'prayer': player.prayer, }
    session.commit()
    session.close()
    return data


def player_owns_weapon(player_id, weapon_name):
    session = Session()
    r = False
    i = session.query(Item).filter(Item.name == weapon_name).first()
    w = session.query(ItemInventory).filter(ItemInventory.user_id == player_id).filter(ItemInventory.item_id == i.id)

    if w.count() > 0:
        if w.first().count > 0:
            r = True

    session.close()
    return r


def item_exists(item_name):
    session = Session()
    i = session.query(exists().where(Item.name == item_name)).scalar()
    session.close()
    return i


def get_rank(user_id):
    session = Session()
    p = session.query(User).filter(User.id == user_id).first()
    rank = p.experience // 1000
    session.close()
    return rank


def get_server_wins(user_id, server_id):
    wins = 0
    session = Session()

    p = session.query(HiscoresReport).filter(HiscoresReport.winner_id == user_id) \
        .filter(HiscoresReport.server_id == server_id)

    for row in p.all():
        wins += row.count

    session.close()
    return wins


def get_global_wins(user_id):
    wins = 0
    session = Session()

    p = session.query(HiscoresReport).filter(HiscoresReport.winner_id == user_id)

    for row in p.all():
        wins += row.count

    session.close()
    return wins


def user_has_enough_gp(user_id, stake):
    session = Session()
    p = session.query(User).filter(User.id == user_id).first()
    gp = p.gp
    session.close()
    return gp >= stake


def get_stake(channel_id):
    session = Session()
    m = session.query(Match).filter(Match.channel_id == channel_id).first()
    r = m.stake
    session.close()
    return r


def get_items():
    items = []
    session = Session()
    i = session.query(Item).all()

    for item in i:
        d = {}
        d['name'] = item.name
        d['description'] = item.description
        d['cost'] = item.price
        d['id'] = item.id
        items.append(d)

    session.close()
    return items


def get_user_gp(user_id):
    session = Session()
    p = session.query(User).filter(User.id == user_id).first()
    gp = p.gp
    session.close()
    return gp


def get_user_inventory(user_id):
    inv = []
    session = Session()
    w = session.query(ItemInventory).filter(ItemInventory.user_id == user_id)

    if w.count() > 0:
        for item in w:
            d = {}
            d['name'] = item.item.name
            d['count'] = item.count
            inv.append(d)

    session.close()
    return inv


def get_global_hiscores():
    session = Session()
    h = session.query(HiscoresReport.winner_id, User.name, func.sum(HiscoresReport.count).label('wins')) \
        .filter(User.id == HiscoresReport.winner_id) \
        .group_by(HiscoresReport.winner_id, User.name) \
        .order_by(text('wins DESC')) \
        .limit(10) \
        .all()
    session.close()
    return h


def get_server_hiscores(server_id):
    session = Session()
    h = session.query(HiscoresReport.winner_id, User.name, func.sum(HiscoresReport.count).label('wins'),
                      HiscoresReport.server_id) \
        .filter(HiscoresReport.winner_id == User.id) \
        .filter(HiscoresReport.server_id == server_id) \
        .group_by(HiscoresReport.winner_id, User.name, HiscoresReport.server_id) \
        .order_by(text('wins DESC')) \
        .limit(10) \
        .all()
    session.close()
    return h
