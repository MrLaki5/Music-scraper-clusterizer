import json
import sqlalchemy
from db.Model import metadata
import os
import threading

# Get path of db configuration
config_path = os.path.join(os.path.dirname(__file__), 'db.json')

# Load db configuration
with open(config_path) as f:
    db_config = json.load(f)
connection_string = 'postgresql://' + db_config['user'] + ':' + db_config['password'] + '@' + db_config['host'] + ":" \
                    + db_config['port'] + "/" + db_config['db']

# Creates connection with db
engine = sqlalchemy.create_engine(connection_string)

synchronization_queue = {
    "album": [],
    "artist": [],
    "song": []
}

synchronization_lock = threading.Lock()


# Recreate all tables in db
def recreate_database():
    # Drops all tables in database
    metadata.drop_all(bind=engine)
    # Creates tables in database that we defined in metadata
    metadata.create_all(bind=engine)


# Execute select query
def check_if_exists_in_db(query, params, type_table=None, should_lock=False):
    with synchronization_lock:
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
            if type_table and type_table in synchronization_queue:
                curr_lock = None
                for site_id in synchronization_queue[type_table]:
                    if params["site_id"] == site_id["item"]:
                        if should_lock:
                            curr_lock = site_id["lock"]
                            break
                if curr_lock:
                    curr_lock.wait()
                else:
                    synchronization_queue[type_table].append({"item": params["site_id"], "lock": threading.Event()})
        connection.close()
    return ret_val


# Execute insert query
def insert_in_db(query, params, type_table=None):
    with synchronization_lock:
        statement = sqlalchemy.sql.text(query)
        connection = engine.connect()
        if params:
            results = connection.execute(statement, params)
        else:
            results = connection.execute(statement)
        if results.rowcount > 0:
            ret_val = results.fetchone()
            ret_val = ret_val["id"]
        else:
            ret_val = None
        connection.close()
        if type_table and type_table in synchronization_queue:
            i = 0
            while i < len(synchronization_queue[type_table]):
                if params["site_id"] == synchronization_queue[type_table][i]["item"]:
                    synchronization_queue[type_table][i]["lock"].set()
                    synchronization_queue[type_table].remove(synchronization_queue[type_table][i])
                    break
                i += 1
    return ret_val


# Remove id from synchronization queue
def remove_item_from_queue(item, type_table):
    with synchronization_queue:
        if type_table not in synchronization_queue:
            return
        i = 0
        while i < len(synchronization_queue[type_table]):
            if item == synchronization_queue[type_table][i]["item"]:
                synchronization_queue[type_table][i]["lock"].set()
                synchronization_queue[type_table].remove(synchronization_queue[type_table][i])
                break
            i += 1


# Execute select query
def check_if_exists_and_add_in_db_return_id(query_select, params_select, query_insert, params_insert):
    with synchronization_lock:
        statement = sqlalchemy.sql.text(query_select)
        connection = engine.connect()
        if params_select:
            results = connection.execute(statement, params_select)
        else:
            results = connection.execute(statement)
        if results.rowcount > 0:
            ret_val = results.fetchone()["id"]
        else:
            statement = sqlalchemy.sql.text(query_insert)
            if params_insert:
                results = connection.execute(statement, params_insert)
            else:
                results = connection.execute(statement)
            if results.rowcount > 0:
                ret_val = results.fetchone()["id"]
            else:
                ret_val = None
        connection.close()
    return ret_val
