from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class PurchaseHistory(Base):
    """ Purchase history"""

    __tablename__ = "purchase_history"

    id = Column(Integer, primary_key=True)
    book_id = Column(String(100), nullable=False)
    purchase_id = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)

    def __init__(self, book_id, purchase_id, username, quantity):
        """ Purchase a book"""
        self.book_id = book_id
        self.purchase_id = purchase_id
        self.username = username
        self.date_created = datetime.datetime.now()
        self.quantity = quantity

    def to_dict(self):
        """ Dictionary Representation of a purchase history """
        purchase_dict = {
            "id": self.id,
            "book_id": self.book_id,
            "purchase_id": self.purchase_id,
            "username": self.username,
            "date_created": self.date_created,
            "quantity": self.quantity
        }
        
        return purchase_dict
