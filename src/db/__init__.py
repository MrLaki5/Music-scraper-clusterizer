import json
import sqlalchemy
from db.Model import metadata
import os
import logging

# Get path of db configuration
config_path = os.path.join(os.path.dirname(__file__), 'db.json')

# Load db configuration
with open(config_path) as f:
    db_config = json.load(f)
connection_string = 'postgresql://' + db_config['user'] + ':' + db_config['password'] + '@' + db_config['host'] + ":" \
                    + db_config['port'] + "/" + db_config['db']

# Creates connection with db
engine = sqlalchemy.create_engine(connection_string)


# Recreate all tables in db
def recreate_database():
    # Drops all tables in database
    metadata.drop_all(bind=engine)
    # Creates tables in database that we defined in metadata
    metadata.create_all(bind=engine)


# Execute select query
def check_if_exists_in_db(query, params):
    statement = sqlalchemy.sql.text(query)
    connection = engine.connect()
    if params:
        results = connection.execute(statement, params)
    else:
        results = connection.execute(statement)
    if results.rowcount > 0:
        ret_val = results.fetchone()
    else:
        ret_val = None
    connection.close()
    return ret_val


# Execute insert query
def insert_in_db(query, params):
    statement = sqlalchemy.sql.text(query)
    connection = engine.connect()
    try:
        if params:
            results = connection.execute(statement, params)
        else:
            results = connection.execute(statement)
    except Exception as ex:
        logging.error("Database insert exception, ex: " + str(ex) +
                      ", query: " + str(query) + ", params: " + str(params))
        results = None
    if results and results.rowcount > 0:
        ret_val = results.fetchone()
        ret_val = ret_val["id"]
    else:
        ret_val = None
    connection.close()
    return ret_val
