from sqlalchemy import Column, Date, Float, Integer, Boolean, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AccountTransaction(Base):
    __tablename__ = 'AccountTransactions'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    amount = Column(Float)

def get_transaction_count_per_month(session):
    transaction_count_per_month = session.query(
        func.extract('year', AccountTransaction.date).label('year'),
        func.extract('month', AccountTransaction.date).label('month'),
        func.count().label('transaction_count')
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    return transaction_count_per_month