from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class BookInventory(Base):
    """ Book inventory """

    __tablename__ = "book_inventory"

    id = Column(Integer, primary_key=True)
    book_id = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, book_id, name, author, category, price, quantity):
        """ add a new book to the online shop inventory"""
        self.book_id = book_id
        self.name = name
        self.author = author
        self.category = category
        self.price = price
        self.quantity = quantity
        self.date_created = datetime.datetime.now()


    def to_dict(self):
        """ Dictionary Representation of a book inventory reading """
        book_dict = {
            "id": self.id,
            "book_id": self.book_id,
            "name": self.name,
            "author": self.author,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
            "date_created": self.date_created
        }

        return book_dict
