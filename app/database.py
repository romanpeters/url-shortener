import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLAlchemyBase = declarative_base()
engine = sa.create_engine("sqlite:///sqlite.db", echo=False)
Session = sessionmaker(bind=engine)


class URL(SQLAlchemyBase):
    __tablename__ = 'URLs'
    url_id = sa.Column(sa.String(8), primary_key=True)
    url = sa.Column(sa.String(2000))
    visits = sa.Column(sa.Integer)
    timestamp = sa.Column(sa.Integer)

    def __repr__(self):
        return f"<URL(url_id='{self.url_id}', url='{self.url}', visits='{self.visits}')>"


SQLAlchemyBase.metadata.create_all(engine)
