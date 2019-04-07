from sqlalchemy import Column, Integer, String, ForeignKey

from .base import Base


class ItemInventory(Base):
    __tablename__ = 'item_inventory'

    user_id = Column(String, ForeignKey('user.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    count = Column(Integer, default=0)

    def __init__(self, user_id, item_id, count):
        self.user_id = user_id
        self.item_id = item_id
        self.count = count
