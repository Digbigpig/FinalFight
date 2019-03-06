from cogs.utils.models.base import Session
from cogs.utils.models.user import User
from cogs.utils.models.player import Player
from cogs.utils.models.item import Item
from cogs.utils.models.role import Role
from cogs.utils.models.server import Server
from cogs.utils.models.channel import Channel
from cogs.utils.models.match import Match
from cogs.utils.models.item_inventory import ItemInventory
from sqlalchemy.sql import exists


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

    if m.turn % 2 == 0:     # Even turns are player 2, odd is player 1
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

    if m.turn % 2 == 0:     # Even turns are player 2, odd is player 1
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

    if m.turn % 2 == 0:     # Even turns are player 2, odd is player 1
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
