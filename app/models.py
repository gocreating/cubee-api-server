import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    password = Column(String(120), unique=True)

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.username)

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'))
    created = Column(DateTime, default=func.now())
    title = Column(String(30))
    body = Column(String(120))

    def __init__(self, author_id=None, title=None, body=None):
        self.author_id = author_id
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Post %r>' % (self.title)
