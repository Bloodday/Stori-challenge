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
    engine = get_engine(DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)
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
        account_total = round(account_total.total + transactions_total, 2)
        session.add(account_total)

    session.commit()

    total_balance = account_total.total

    transaction_count_per_month = session.query(
        func.extract('year', AccountTransaction.date).label('year'),
        func.extract('month', AccountTransaction.date).label('month'),
        func.count().label('transaction_count')
    ).group_by('year', 'month').order_by('year', 'month').all()

    average_debit = round(session.query(func.avg(AccountTransaction.amount)).filter(AccountTransaction.amount < 0).scalar(),2)
    average_credit = round(session.query(func.avg(AccountTransaction.amount)).filter(AccountTransaction.amount > 0).scalar(),2)

    # Close the session
    session.close()
    
    engine.dispose()

    account_summary = construct_message(transaction_count_per_month, total_balance, average_debit, average_credit) 
    print(account_summary)
    SendEmail(account_summary)

    return

def construct_message(transaction_count_per_month, total_balance, average_debit, average_credit):
    result = ""

    total_balance_message = f"Total balance is {total_balance}"
    
    transactions_per_month_messages = []
    # Print the results
    for row in transaction_count_per_month:
        year = row.year
        month = row.month
        transaction_count = row.transaction_count
        transactions_per_month_messages.append(f"Number of transactions in {year}/{month}: {transaction_count}")

    average_debit_message = f"Average debit amount: {average_debit}" 
    average_credit_message = f"Average debit amount: {average_credit}" 

    result += total_balance_message + "\n"

    for montly_transactions_message in transactions_per_month_messages:
        result += montly_transactions_message + "\n"

    result += average_debit_message + "\n"
    result += average_credit_message + "\n"
    return result

lambda_handler(None, None)