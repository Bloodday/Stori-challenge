import os
import csv
import datetime
from sqlalchemy import create_engine, exists, func
from sqlalchemy_utils import database_exists, create_database 
from sqlalchemy.orm import sessionmaker
from DatabaseModels.AccountTransaction import AccountTransaction
from DatabaseModels.AccountsBalance import AccountBalance
from Services.EmailService import SendEmail

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']

# Configurar la conexión a la base de datos PostgreSQL
def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=50, echo=False)
    return engine

def lambda_handler(event, context):
    engine = get_engine(DB_USER,DB_PASSWORD,"localhost","5432","Accounts")
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

    # Store the updated total balance of the account
    account_total = session.query(AccountBalance).first()
    if account_total:
        account_total.total = round(account_total.total + transactions_total, 2)
    else:
        account_total = AccountBalance(total=transactions_total)
        session.add(account_total)

    session.commit() 

    result = session.query(
        func.extract('year', AccountTransaction.date).label('year'),
        func.extract('month', AccountTransaction.date).label('month'),
        func.count().label('transaction_count')
    ).group_by('year', 'month').order_by('year', 'month').all()

    # Print the results
    for row in result:
        year = row.year
        month = row.month
        transaction_count = row.transaction_count
        print(f"{year}/{month}: {transaction_count} transactions")

    # Close the session
    session.close()

    SendEmail()

    return "Hello!"    

lambda_handler(None, None)