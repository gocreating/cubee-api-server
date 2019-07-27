import click

from flask import current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import get_config

config = get_config()
engine = create_engine(config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
db_session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
))
Base = declarative_base()
Base.query = db_session.query_property()

def get_db():
    if 'db_session' not in g:
        g.db_session = db_session

    return g.db_session

def close_db(e=None):
    db_session = g.pop('db_session', None)

    if db_session is not None:
        db_session.remove()

def init_db():
    db_session = get_db()
    import app.models

    Base.metadata.create_all(bind=engine)

    from app.models import User
    u = User('admin', 'pass')
    db_session.add(u)
    db_session.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
