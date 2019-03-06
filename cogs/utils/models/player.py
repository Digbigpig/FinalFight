from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from .base import Base


class Player(Base):
    __tablename__ = 'player'

    # A user can have many different player data's
    user_id = Column(String, ForeignKey('user.id'), nullable=True)
    user = relationship("User", backref=backref('players', uselist=True))

    # A match has multiple players
    match_id = Column(Integer, ForeignKey('match.id', ondelete='CASCADE'), primary_key=True)
    match = relationship("Match", backref=backref("players", cascade="save-update, merge, delete"))
    position = Column(Integer, primary_key=True)

    hp = Column(Integer, default=100)
    special = Column(Integer, default=100)
    prayer = Column(String)
    food = Column(String, default=3)
    frozen = Column(Boolean, default=False)
    poison = Column(Boolean, default=False)
    prayer_points = Column(Integer, default=100)

    def __init__(self, match, position):
        self.match = match
        self.position = position
