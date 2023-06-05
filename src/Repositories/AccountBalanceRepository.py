from DatabaseModels.AccountsBalance import AccountBalance
from sqlalchemy.orm import Session

def update_account_balance(session: Session, transactions_total: int):
    account_total = session.query(AccountBalance).first()
    if account_total:
        account_total.total = round(account_total.total + transactions_total, 2)
    else:
        account_total = AccountBalance(total=round(transactions_total,2))
        session.add(account_total)
    return account_total