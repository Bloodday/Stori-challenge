import os
import csv
import time
import datetime
from sqlalchemy.orm import sessionmaker
from DatabaseModels.AccountTransaction import get_transaction_count_per_month
from Repositories.AccountBalanceRepository import update_account_balance
from Repositories.AccountTransactionsRepository import get_average_credit, get_average_debit, insert_if_not_exist
from Services.DatabaseService import get_engine
from DatabaseModels.AccountsBalance import AccountBalance
from Services.EmailService import SendEmail

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']


def lambda_handler(event, context):
    engine = get_engine(DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)
    Session = sessionmaker(bind=engine)
    session = Session()

    folder_path = './data'  # Replace with the path to your folder

    transactions_to_insert = []
    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):  # Check if the file is a CSV file
            process_file(session, folder_path, transactions_to_insert, filename)
                    

    # calculates the total amount in the transactionr processed
    transactions_total = round(sum(transaction.amount for transaction in transactions_to_insert),2)

    # Store the updated total balance of the account
    account_total = update_account_balance(session, transactions_total)

    session.commit()

    total_balance = account_total.total

    transaction_count_per_month = get_transaction_count_per_month(session)

    average_debit = get_average_debit(session)
    average_credit = get_average_credit(session)

    # Close the session
    session.close()
    
    engine.dispose()

    account_summary = construct_message(transaction_count_per_month, total_balance, average_debit, average_credit) 
    print(account_summary)
    SendEmail(account_summary)
    return

def process_file(session, folder_path, transactions_applied, filename):
    file_path = os.path.join(folder_path, filename)
    # Read the CSV file and store transactions in the db
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # ignore the header

        for row in reader:
            transaction_id = int(row[0])
            date = datetime.datetime.strptime(row[1], '%Y/%m/%d').date()
            amount = float(row[2])
            
            was_inserted, transaction = insert_if_not_exist(session, transaction_id, date, amount)
            if (was_inserted):
                transactions_applied.append(transaction)
            else:
                print(f"Skipping transaction with ID {transaction_id} as it already exists.")

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

time.sleep(60)