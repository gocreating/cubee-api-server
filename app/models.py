import sqlalchemy as sa
import datetime

metadata = sa.MetaData()

users = sa.Table('users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(50), unique=True),
    sa.Column('password', sa.String(120)),
)

posts = sa.Table('posts', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('author_id', None, sa.ForeignKey('users.id')),
    sa.Column('created_ts', sa.TIMESTAMP, default=datetime.datetime.utcnow),
    sa.Column('updated_ts', sa.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow),
    sa.Column('title', sa.String(100)),
    sa.Column('body', sa.JSON),
)
