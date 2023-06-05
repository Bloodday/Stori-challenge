from sqlalchemy import Column, Date, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AccountBalance(Base):
    __tablename__ = 'AccountsBalance'
    id = Column(Integer, primary_key=True)
    total = Column(Float, default=0.0)