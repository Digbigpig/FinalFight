from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from .base import Base
from .item_inventory import ItemInventory


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    users = relationship('ItemInventory', backref='item', primaryjoin=id == ItemInventory.item_id)

    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price
