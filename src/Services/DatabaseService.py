from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from DatabaseModels.AccountTransaction import AccountTransaction
from DatabaseModels.AccountsBalance import AccountBalance 

# Configurar la conexión a la base de datos PostgreSQL
def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=50, echo=False)
    AccountTransaction.metadata.create_all(engine)
    AccountBalance.metadata.create_all(engine)
    return engine