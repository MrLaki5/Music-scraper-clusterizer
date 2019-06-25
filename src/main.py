import db
import logging
import scraper
import datetime

# Logger configuration for both console and file
FILE_LOG = True
CONSOLE_LOG = True

if __name__ == '__main__':
    log_name = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S') + ".log"
    if FILE_LOG:
        logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler('./logs/' + log_name, 'w', 'utf-8')])
        if CONSOLE_LOG:
            logging.getLogger().addHandler(logging.StreamHandler())
    else:
        if CONSOLE_LOG:
            logging.basicConfig(level=logging.INFO)
    logging.info("Logger started!")


work_flag = True
while work_flag:
    print("--------------------------")
    print("Menu:")
    print("1. Scrape data")
    print("2. Exit")
    print("--------------------------")
    user_input = input("Choose: ")
    if user_input == "1":
        db.recreate_database()
        logging.info("Database recreated, starting scrape, time: " + str(datetime.datetime.now()))
        scraper.scrape_country("Yugoslavia")
    elif user_input == "2":
        work_flag = False





# statement = sqlalchemy.sql.text(""" INSERT INTO album_group DEFAULT VALUES""")
# ret = db.engine.connect().execute(statement)

#statement = sqlalchemy.sql.text(""" INSERT INTO artist_name(id_artist, name) VALUES(1, 'Bora Corba') """)
#db.engine.connect().execute(statement)

#statement = sqlalchemy.sql.text(""" INSERT INTO artist_name(id_artist, name) VALUES(1, 'Riblja Corba') """)
#db.engine.connect().execute(statement)


# print(model.album.columns)
#statement = sqlalchemy.sql.text(""" SELECT artist.id, artist_name.name FROM artist, artist_name WHERE artist.id = artist_name.id_artist""")
#results = db.engine.connect().execute(statement)
#for res in results:
#    print(res)
