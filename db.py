from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    queue = relationship("Queue", back_populates="user", useList=False)
    
    def __repr__(self):
        return f'User {self.id}'
        
class Queue(Base):
    __tablename__ = 'queue'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="queue")

    creation_time = Column(DateTime, default=func.now())

    def __repr__(self):
        return f'Queue {self.id}'

def start():
    engine = create_engine('sqlite:///:memory:')

    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)
    return engine, session