from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from .base import Base
from .hiscores_report import HiscoresReport
from .item_inventory import ItemInventory


class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    name = Column(String)
    rank = Column(Integer)
    experience = Column(Integer, default=0)
    gp = Column(Integer)
    items = relationship("ItemInventory", backref='user', primaryjoin=id == ItemInventory.user_id)
    wins = relationship("HiscoresReport", back_populates="winner", primaryjoin=id == HiscoresReport.winner_id)
    loses = relationship("HiscoresReport", back_populates="loser", primaryjoin=id == HiscoresReport.loser_id)

    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name
        self.rank = 0
        self.gp = 1000
