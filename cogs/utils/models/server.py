from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base
from .hiscores_report import HiscoresReport


class Server(Base):
    __tablename__ = 'server'

    id = Column(String, primary_key=True)
    name = Column(String)
    hiscores = relationship("HiscoresReport", back_populates="server", primaryjoin=id == HiscoresReport.server_id)

    def __init__(self, server_id, name):
        self.id = server_id
        self.name = name
