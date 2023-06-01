import csv
import datetime
from sqlalchemy import create_engine, exists
from sqlalchemy_utils import database_exists, create_database 
from sqlalchemy.orm import sessionmaker
from DatabaseModels.AccountTransaction import AccountTransaction
from DatabaseModels.AccountsBalance import AccountBalance


# Configurar la conexión a la base de datos PostgreSQL
def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=50, echo=False)
    return engine

def lambda_handler(event, context):
    engine = get_engine("postgres","your_password","localhost","5432","Accounts")
    AccountTransaction.metadata.create_all(engine)
    AccountBalance.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Read the CSV file and store transactions in the db
    with open('transactions.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # ignore the header

        transactions_applied = [] 
        for row in reader:
            id_transaccion = int(row[0])
            fecha = datetime.datetime.strptime(row[1], '%Y/%m/%d').date()
            monto = float(row[2])

            # Check if the transaction ID already exists in the database
            transaction_exists = session.query(exists().where(AccountTransaction.id == id_transaccion)).scalar()
            if transaction_exists:
                print(f"Skipping transaction with ID {id_transaccion} as it already exists.")
                continue

            transaction = AccountTransaction(id=id_transaccion, date=fecha, amount=monto)
            session.add(transaction)
            transactions_applied.append(transaction)

    # calculates the transactions balance
    transactions_total = round(sum(transaction.amount for transaction in transactions_applied),2)

    for transaction in transactions_applied:
        transaction.isApplied = True

    # Store the modify the total balance of the account
    account_total = session.query(AccountBalance).first()
    if account_total:
        account_total.total = round(account_total.total + transactions_total, 2)
    else:
        account_total = AccountBalance(total=transactions_total)
        session.add(account_total)

    session.commit() 

    return "Hello!"    

lambda_handler(None, None)