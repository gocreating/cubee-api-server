import sqlalchemy as sa
from sqlalchemy.sql import func

metadata = sa.MetaData()

users = sa.Table('users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(50), unique=True),
    sa.Column('password', sa.String(120), unique=True),
)

posts = sa.Table('posts', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('author_id', None, sa.ForeignKey('users.id')),
    sa.Column('created', sa.DateTime, default=func.now()),
    sa.Column('title', sa.String(100)),
    sa.Column('body', sa.JSON),
)
