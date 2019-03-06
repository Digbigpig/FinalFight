from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from .base import Base


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(String, primary_key=True)
    name = Column(String)
    server_id = Column(String, ForeignKey('server.id', ondelete='CASCADE'))
    server = relationship("Server", backref=backref("channels", cascade="save-update, merge, delete"))

    def __init__(self, channel_id, name, server):
        self.id = channel_id
        self.name = name
        self.server = server
