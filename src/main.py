import db
import sqlalchemy
import db.Model as model
import logging

# Logger configuration
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Logger started!")


db.recreate_database()




# statement = sqlalchemy.sql.text(""" INSERT INTO album_group DEFAULT VALUES""")
# ret = db.engine.connect().execute(statement)

#statement = sqlalchemy.sql.text(""" INSERT INTO artist_name(id_artist, name) VALUES(1, 'Bora Corba') """)
#db.engine.connect().execute(statement)

#statement = sqlalchemy.sql.text(""" INSERT INTO artist_name(id_artist, name) VALUES(1, 'Riblja Corba') """)
#db.engine.connect().execute(statement)


print(model.album.columns)
#statement = sqlalchemy.sql.text(""" SELECT artist.id, artist_name.name FROM artist, artist_name WHERE artist.id = artist_name.id_artist""")
#results = db.engine.connect().execute(statement)
#for res in results:
#    print(res)
