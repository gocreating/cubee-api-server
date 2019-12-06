from sqlalchemy import create_engine
from app.models import metadata

def init_app(app):
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(db_uri)
    metadata.create_all(engine)
    return engine
