from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from .base import Base


class Match(Base):
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, ForeignKey('channel.id', ondelete='CASCADE'))
    channel = relationship("Channel", backref=backref("match", uselist=False, cascade="save-update, merge, delete"))

    wait = Column(Boolean, default=False)
    rules = Column(String)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    last_play = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    turn = Column(Integer, default=0)

    def __init__(self, channel):
        self.channel = channel
