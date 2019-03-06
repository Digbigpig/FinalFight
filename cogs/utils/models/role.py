from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Role(Base):
    __tablename__ = 'role'

    id = Column(String, primary_key=True)
    name = Column(String)
    server_id = Column(String, ForeignKey('server.id'))
    server = relationship("Server", backref="roles")

    def __init__(self, role_id, name, server):
        self.id = role_id
        self.name = name
        self.server = server
