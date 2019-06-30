import db
import logging
import scraper
import datetime
import time
import plotting_results

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
    print("4. Plot data")
    print("5. Exit")
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
            print("4. Person rating, top 100")
            print("5. Person vocals, top 100")
            print("6. Person category 'arranged by' count, top 100")
            print("7. Person category 'lyrics by' count, top 100")
            print("8. Person category 'music by' count, top 100")
            print("9. Song on album count, top 100")
            print("10. Get artists with their sites")
            print("11. Back")
            print("--------------------------")
            query_num = input("Choose: ")
            if query_num == "1":
                results = db.get_album_count_by_order()
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "2":
                results = db.get_album_count_by_style()
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "3":
                results = db.get_album_count_by_versions_top_20()
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "4":
                results = db.get_person_count_by_rating_top_100()
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "5":
                results = db.get_person_count_by_vocals_top_100()
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "6":
                results = db.get_person_count_by_category_top_100("arranged")
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "7":
                results = db.get_person_count_by_category_top_100("lyrics")
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "8":
                results = db.get_person_count_by_category_top_100("music")
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "9":
                results = db.get_song_on_album_count_top_100()
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "10":
                results = db.get_artist_sites()
                logging.info(str(results.keys()))
                for result in results:
                    logging.info(str(result))
                time.sleep(0.1)
            elif query_num == "11":
                loc_w_flag = False
    elif user_input == "4":
        loc_w_flag = True
        while loc_w_flag:
            print("--------------------------")
            print("Choose plotting:")
            print("1. Genres count, top 6")
            print("2. Song count, grouped by song length")
            print("3. Album count group by decades")
            print("4. Album count group by is name written in cyrillic")
            print("5. Album count grouped by genres number of album")
            print("6. Back")
            print("--------------------------")
            query_num = input("Choose: ")
            if query_num == "1":
                results = db.get_album_count_by_genres_top_6()
                plotting_results.plot_results_x_string(results, "Genres count, top 6")
            elif query_num == "2":
                results = db.get_song_duration_count()
                x_arr = ["<90", "91-180", "181-240", "241-300", "301-360", ">361"]
                y_arr = []
                for result in results:
                    for item in result:
                        y_arr.append(item)
                plotting_results.plot(x_arr, y_arr, "Song count, grouped by song length")
            elif query_num == "3":
                results = db.get_album_count_by_decades()
                plotting_results.plot_results_x_string(results, "Album count group by decades")
            elif query_num == "4":
                results = db.get_album_count_by_is_cyrillic()
                plotting_results.plot_results_x_string(results,
                                                       "Album count group by is name written in cyrillic", True)
            elif query_num == "5":
                results = db.get_album_count_grouped_by_number_of_genres()
                x_arr = ["1 genre", "2 genres", "3 genres", "4 or more genres"]
                y_arr = []
                for result in results:
                    for item in result:
                        y_arr.append(item)
                plotting_results.plot(x_arr, y_arr, "Album count grouped by genres number of album", True)
            elif query_num == "6":
                loc_w_flag = False
    elif user_input == "5":
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
