import os, sys, inspect
from cogs.utils.models.base import Session, engine, Base
# from ..models.channel import Channel
# from ..models.server import Server
# from ..models.user import User
# from ..models.player import Player
# from ..models.match import Match
# from ..models.item_inventory import ItemInventory
# from ..models.item import Item
# from ..models.hiscores_report import HiscoresReport

# 2 - generate database schema
Base.metadata.create_all(engine)


def rebuild_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    rebuild_db()

# 3 - create a new session
session = Session()
# s = Server('376168624983113728')
# r = Role("testid", "TestRole", s)

# session.add(r)
session.commit()
session.close()
# # 4 - create server
# server = Server('qwerdfsftsdfy1234', 'Test Server')
#
# # 5 - creates channel
# general = Channel("qwertassdfsfdsdff", "General", server)
# afk = Channel("qwertdfghsdfsdffsdfff", "Afk", server)
#
# # Create matches
# general_match = Match(general)
# afk_match = Match(afk)
#
# # Create players
# p1 = Player(None, general_match, 1)
# p2 = Player(None, general_match, 2)
# p3 = Player(None, afk_match, 1)
# p4 = Player(None, afk_match, 2)
#
# # Create Users
# user1 = User("richardid", "Richard")
# user2 = User("katysid3", "Katy")
#
# # Create Items
# scim = Item("Rune Scim", "a rune scimitar found in the wilderness")
#
# # Add item to user
# inv1 = ItemInventory(user=user1, item=scim, count=15)
# inv2 = ItemInventory(user=user2, item=scim, count=150)
#
# # Make a hiscores record
# hiscore = HiscoresReport(winner=user1, loser=user2, server=server, count=10)
#
# # 9 - persists data
# session.add(server)
#
# session.add(general)
# session.add(afk)
#
# session.add(afk_match)
# session.add(general_match)
#
# session.add(p1)
# session.add(p2)
# session.add(p3)
# session.add(p4)
#
# session.add(user1)
# session.add(user2)
#
# session.add(scim)
# session.add(inv1)
# session.add(inv2)
#
# session.add(hiscore)
#
# # 10 - commit and close session
# session.commit()
# session.close()
