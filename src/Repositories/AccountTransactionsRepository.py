import typing
from DatabaseModels.AccountTransaction import AccountTransaction
from sqlalchemy import exists, func

def insert_if_not_exist(session, transaction_id, date, amount) -> typing.Tuple[bool, AccountTransaction]: 
    transaction_exists = session.query(exists().where(AccountTransaction.id == transaction_id)).scalar()
    if transaction_exists:
        print(f"Skipping transaction with ID {transaction_id} as it already exists.")
        return False, None
    
    transaction = AccountTransaction(id=transaction_id, date=date, amount=amount)
    session.add(transaction)
    return True, transaction

def get_average_credit(session):
    return round(session.query(func.avg(AccountTransaction.amount)).filter(AccountTransaction.amount > 0).scalar(),2)

def get_average_debit(session):
    average_debit = round(session.query(func.avg(AccountTransaction.amount)).filter(AccountTransaction.amount < 0).scalar(),2)
    return average_debit