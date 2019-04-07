from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class HiscoresReport(Base):
    __tablename__ = 'hiscores'

    winner_id = Column(String, ForeignKey('user.id'), primary_key=True)
    winner = relationship("User", back_populates="wins", foreign_keys=[winner_id])
    loser_id = Column(String, ForeignKey('user.id'), primary_key=True)
    loser = relationship("User", back_populates="loses", foreign_keys=[loser_id])
    server_id = Column(String, ForeignKey('server.id'), primary_key=True)
    server = relationship("Server", back_populates='hiscores', foreign_keys=[server_id])
    count = Column(Integer, default=0)

    def __init__(self, winner_id, loser_id, server_id):
        self.winner_id = winner_id
        self.loser_id = loser_id
        self.server_id = server_id
