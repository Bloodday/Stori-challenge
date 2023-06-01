from sqlalchemy import Column, Date, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AccountTransaction(Base):
    __tablename__ = 'AccountTransactions'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    amount = Column(Float)
    isApplied = Column(Boolean, default=False)

