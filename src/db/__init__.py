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
    statement = sqlalchemy.sql.text("""
    SELECT count(*), 
    g.content as genre 
    FROM album_genre as g 
    GROUP BY g.content
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get albums count ordered by style
def get_album_count_by_style():
    statement = sqlalchemy.sql.text("""
    SELECT count(*), 
    s.content as style 
    FROM album_style as s 
    GROUP BY s.content
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get albums count by versions top 20
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


# Get person count by rating top 100
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


# Get person count by vocals top 100
def get_person_count_by_vocals_top_100():
    statement = sqlalchemy.sql.text("""
    WITH cte AS (
        SELECT rank() OVER (ORDER BY a.vocals DESC) AS rnk,
        a.vocals as vocals,
        a.name as name
        FROM artist as a 
        WHERE a.is_group = False AND a.vocals IS NOT NULL
    )
    SELECT *
    FROM   cte
    WHERE  rnk <= 100 
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get person count by category top 100
def get_person_count_by_category_top_100(type_aos):
    statement = sqlalchemy.sql.text("""
    WITH cte AS (
        SELECT rank() OVER (ORDER BY count(*) DESC) AS rnk,
        count(*) AS cnt,
        (SELECT b.name 
        FROM artist AS b 
        WHERE a.id = b.id 
        LIMIT 1) as name
        FROM artist AS a, artist_on_song AS aos
        WHERE a.is_group = False and a.id = aos.id_artist and aos.type = '""" + type_aos + """'
        GROUP BY a.id
    )
    SELECT *
    FROM   cte
    WHERE  rnk <= 100 
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get song on album count top 100
def get_song_on_album_count_top_100():
    statement = sqlalchemy.sql.text("""
    WITH cte AS (
        SELECT rank() OVER (ORDER BY COUNT(*) DESC) AS rnk,
        COUNT(*) AS cnt,
        (SELECT b.name 
        FROM song AS b 
        WHERE soa.id = b.id 
        LIMIT 1) as name,
        (SELECT string_agg(DISTINCT gen.content, ', ')
        FROM album_genre AS gen
        WHERE gen.id_album = soa.id_album) AS genres,
        (SELECT string_agg(DISTINCT sty.content, ', ')
        FROM album_style AS sty
        WHERE sty.id_album = soa.id_album) AS styles,
        (SELECT string_agg(DISTINCT form.content, ', ')
        FROM album_format AS form
        WHERE form.id_album = soa.id_album) AS formats,
        (SELECT string_agg(DISTINCT alb.year::TEXT, ', ')
        FROM album AS alb
        WHERE alb.id = soa.id_album) AS years,
        (SELECT string_agg(DISTINCT alb.country, ', ')
        FROM album AS alb
        WHERE alb.id = soa.id_album) AS countries 
        FROM song_on_album AS soa
        GROUP BY soa.id
    )
    SELECT *
    FROM   cte
    WHERE  rnk <= 100 
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get artist sites
def get_artist_sites():
    statement = sqlalchemy.sql.text("""
    SELECT a.name, 
    a.is_group, 
    s.web 
    FROM artist_web AS s, artist AS a
    WHERE s.id_artist = a.id
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# QUERIES USED IN PLOTTING #################################


# Get albums count by genres top 6
def get_album_count_by_genres_top_6():
    statement = sqlalchemy.sql.text("""
    WITH cte AS (
        SELECT rank() OVER (ORDER BY count(*) DESC) AS rnk,
        COUNT(*) as cnt,
        gen.content as name
        FROM album_genre as gen 
        GROUP BY gen.content 
    )
    SELECT cnt, name
    FROM   cte
    WHERE  rnk <= 20 
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get albums count by decades
def get_album_count_by_decades():
    statement = sqlalchemy.sql.text("""
    SELECT count(*) as cnt,
    a.decade as decade
    FROM album as a 
    WHERE a.decade IS NOT NULL 
    GROUP BY a.decade 
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results


# Get albums count by is_cyrillic
def get_album_count_by_is_cyrillic():
    statement = sqlalchemy.sql.text("""
    SELECT count(*) as cnt,
    a.is_cyrillic as is_cyrillic
    FROM album as a 
    GROUP BY a.is_cyrillic 
    """)
    connection = engine.connect()
    results = connection.execute(statement)
    connection.close()
    return results
