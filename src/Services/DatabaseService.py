from sqlalchemy import create_engine, text as tx
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import ProgrammingError, OperationalError

from DatabaseModels.AccountTransaction import AccountTransaction
from DatabaseModels.AccountsBalance import AccountBalance 

# Configurar la conexión a la base de datos PostgreSQL
def get_engine(user, passwd, host, port, db):
    print("Se intentará conectar con la base de de datos")
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    print(f"host: {host}, port: {port}, database: {db}")
    engine = create_engine(url, pool_size=50, echo=False,connect_args = {'connect_timeout': 10})
    
    try:
        
        text = "SELECT 1 FROM pg_database WHERE datname='%s'" % db
        for db in (db, 'postgres', 'template1', 'template0', None):
            try:
                it_exist =  bool(_get_scalar_result(engine, tx(text)))
                print("database exist")
                return it_exist
            except (ProgrammingError) as ex:
                if hasattr(ex, 'message'):
                    print(ex.message)
                else:
                    print(ex)
        return False

        
    finally:
        if engine:
            engine.dispose()


    if not database_exists(url,):
        print("La base de dato no existe")
        create_database(url)
        print("Se creo la base de datos")
    
    AccountTransaction.metadata.create_all(engine)
    AccountBalance.metadata.create_all(engine)
    return engine

def _get_scalar_result(engine, sql):
    with engine.connect() as conn:
        return conn.scalar(sql)
