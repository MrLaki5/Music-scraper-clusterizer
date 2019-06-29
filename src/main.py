import db
import logging
import scraper
import datetime
import time

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
    # Wait for logger to be printed
    time.sleep(0.1)


# Main menu part
work_flag = True
while work_flag:
    print("--------------------------")
    print("Menu:")
    print("1. Recreate database")
    print("2. Scrape data")
    print("3. Do queries")
    print("4. Exit")
    print("--------------------------")
    user_input = input("Choose: ")
    if user_input == "1":
        db.recreate_database()
        logging.info("Database recreated")
        time.sleep(0.1)
    elif user_input == "2":
        logging.info("Starting scrape, time: " + str(datetime.datetime.now()))
        scraper.scrape_country("Yugoslavia")
        scraper.scrape_country("Serbia")
        time.sleep(0.1)
    elif user_input == "3":
        loc_w_flag = True
        while loc_w_flag:
            print("--------------------------")
            print("Choose query:")
            print("1. Album count per genre")
            print("2. Album count per style")
            print("3. Album version count, top 20")
            print("4. Person rating count, top 100")
            print("6. Back")
            print("--------------------------")
            query_num = input("Choose: ")
            if query_num == "1":
                results = db.get_album_count_by_order()
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "2":
                results = db.get_album_count_by_style()
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "3":
                results = db.get_album_count_by_versions_top_20()
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "4":
                results = db.get_person_count_by_rating_top_100()
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "6":
                loc_w_flag = False
    elif user_input == "4":
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
