from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .item_inventory import ItemInventory
from .base import Base


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    users = relationship('ItemInventory', backref='item', primaryjoin=id == ItemInventory.item_id)

    def __init__(self, name, description):
        self.name = name
        self.description = description
