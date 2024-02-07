from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Table():
    """
    Base class of all tables. 
    """
    @classmethod
    def to_instance(cls, row):
        return cls.instance_class(row)

    @classmethod
    def filter(cls, session, query, portion=None):
        if portion in [None, "all"]:
            return [self.to_instance(row) for row in session.query(self).filter(query).all()]
        elif portion == "first":
            return self.to_instance(session.query(self).filter(query).first())
        elif portion == "one":
            return self.to_instance(session.query(self).filter(query).one())
            
    def add(self, session):
        session.add(self)
        session.commit()

class Actor():
    def __init__(self, table):
        self.table = table

    def to_json(self, item):
        return {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": self.table.activity_type,
        }

class User(Actor):
    """
    """
    def to_json(self):
        retval = super().to_json()
        retval.update({
            "id": self.id,
            "name": self.name,
            "preferredUsername": self.preferredUsername,
            "summary": self.summary,
            "inbox": self.inbox,
            "outbox": self.outbox,
            "followers": self.followers,
            "following": self.following,
            "liked": self.liked
        })

class Users(Table, Base):
    """
    Interface to the User table.
    """
    __tablename__ = 'user'
    activity_type = "Person"
    instance_class = User
                      
    ## Table columns:
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    preferredUsername = Column(String(250))
    summary = Column(String(250))
    inbox = Column(String(250))
    outbox = Column(String(250))
    followers = Column(String(250))
    following = Column(String(250))
    liked = Column(String(250))
