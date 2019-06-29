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


# Get albums count ordered by genre
def get_album_count_by_order():
    statement = sqlalchemy.sql.text("""SELECT count(*), g.content FROM album_genre as g GROUP BY g.content""")
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get albums count ordered by style
def get_album_count_by_style():
    statement = sqlalchemy.sql.text("""SELECT count(*), s.content FROM album_style as s GROUP BY s.content""")
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get albums count ordered by style
def get_album_count_by_versions_top_20():
    statement = sqlalchemy.sql.text("""
    WITH cte AS (
        SELECT rank() OVER (ORDER BY count(*) DESC) AS rnk,
        COUNT(*) as cnt,
        (SELECT b.name 
        FROM album as b 
        WHERE a.id_album_group = b.id_album_group 
        LIMIT 1) as name
        FROM album as a  
        GROUP BY a.id_album_group 
    )
    SELECT *
    FROM   cte
    WHERE  rnk <= 20 
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get albums count ordered by style
def get_person_count_by_rating_top_100():
    statement = sqlalchemy.sql.text("""
    WITH cte AS (
        WITH inner_cte AS (
            SELECT a1.rating AS rating, 
            art1.id AS id
            FROM album as a1, artist_rating as ar1, artist as art1 
            WHERE ar1.id_album = a1.id and art1.id = ar1.id_artist and art1.is_group = False and a1 IS NOT NULL
        )
        SELECT rank() OVER (ORDER BY AVG(inn.rating) DESC) AS rnk,
        AVG(inn.rating) AS avg_rating,
        (SELECT b.name 
        FROM artist AS b 
        WHERE inn.id = b.id 
        LIMIT 1) as name
        FROM inner_cte inn
        GROUP BY inn.id
    )
    SELECT *
    FROM   cte
    WHERE  rnk <= 100 
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results
