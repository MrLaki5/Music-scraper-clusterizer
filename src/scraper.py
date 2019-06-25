from bs4 import BeautifulSoup
import requests
import logging
import re
import urllib.parse as urlparse
import db
import unicodedata as ud
import threading
import time

album_count_lock = threading.Lock
album_count = 0


# Functions for checking if string is in cyrillic or latin letters
def is_latin(uchr):
    latin_letters = {}
    try:
        return latin_letters[uchr]
    except KeyError:
        return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))


def only_roman_chars(unistr):
    return all(is_latin(uchr) for uchr in unistr if uchr.isalpha())  # isalpha suggested by John Machin


# Logger configuration
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.debug("Logger started!")

REQUEST_STATUS_OK = 200

BASE_URL = "https://www.discogs.com"
BASE_URL_SEARCH = "https://www.discogs.com/search/"
FAST_LAYOUT_ATTR = "layout=sm"
GENRE_ATTR = "genre_exact="
DECADE_ATTR = "decade="
COUNTRY_ATTR = "country_exact="
PAGE_NUM_ATTR = "page="
LIMIT_MAX_ATTR = "limit=250"


# Gets all data for one country, iterating through decades and genre
def scrape_country(country):
    url = BASE_URL_SEARCH + "?" + COUNTRY_ATTR + country + "&" + FAST_LAYOUT_ATTR
    response = requests.get(url)
    if response.status_code == REQUEST_STATUS_OK:
        album_counter = 0
        # Create html_tree of all page
        html_tree = BeautifulSoup(response.text, "html.parser")
        # Get side filter menu
        decades_html_tree = html_tree.find("div", {"id": "page_aside"})
        # Get decade part of filter menu
        decades_html_tree = decades_html_tree.find_all('a', href=re.compile("decade"))
        decades = []
        # Get year from every decade part
        for item in decades_html_tree:
            decades.append(str(int(item.find("small").next.next)))
        logging.debug("Decades: " + str(decades))
        for item in decades:
            album_counter = scrape_country_decade(country, item, album_counter)
        logging.info("Albums scraped, country: " + country + ", album count: " + str(album_count))
    else:
        logging.error("scraper:scrape_country: response status: " + str(response.status_code) + ", on url: " + url)


# Gets all data for one country, for one specific decade
def scrape_country_decade(country, decade, album_counter):
    url = BASE_URL_SEARCH + "?" + COUNTRY_ATTR + country + "&" + DECADE_ATTR + decade + "&" + FAST_LAYOUT_ATTR
    response = requests.get(url)
    if response.status_code == REQUEST_STATUS_OK:
        # Create html_tree of all page
        html_tree = BeautifulSoup(response.text, "html.parser")
        # Get side filter menu
        genre_html_tree = html_tree.find("div", {"id": "page_aside"})
        # Get genre part of filter menu
        genre_html_tree = genre_html_tree.find_all('a', href=re.compile("genre_exact"))
        genres = []
        # Get genre from every genre part
        for item in genre_html_tree:
            temp_genre = re.search('genre_exact=(.+?)&amp;', str(item))
            if temp_genre:
                temp_genre = temp_genre.group(1)
                genres.append(temp_genre)
        if len(genres) > 0:
            logging.debug("scraper:scrape_country_decade: genres found: country: " + country + ", decade: "
                          + decade + ", genres: " + str(genres))
            for item in genres:
                album_counter = scrape_country_decade_genre(country, decade, item, album_counter)
        else:
            logging.debug("scraper:scrape_country_decade: no genres found: country: " + country + ", decade: " + decade)
            album_counter = scrape_country_decade_genre(country, decade, album_counter)
    else:
        logging.error("scraper:scrape_country_decade: response status: " +
                      str(response.status_code) + ", on url: " + url)
    return album_counter


# Gets all data for one country, for one specific decade, for one specific genre
def scrape_country_decade_genre(country, decade, genre=None, album_counter=0):
    work_flag = True
    page_num = 0
    while work_flag:
        page_num += 1
        # Build url
        url = (BASE_URL_SEARCH + "?" + COUNTRY_ATTR + country + "&" + DECADE_ATTR + decade + "&" +
               FAST_LAYOUT_ATTR + "&" + PAGE_NUM_ATTR + str(page_num) + "&" + LIMIT_MAX_ATTR)
        if genre:
            url += "&" + GENRE_ATTR + genre
        response = requests.get(url)
        if response.status_code == REQUEST_STATUS_OK:
            # Create html_tree of all page
            html_tree = BeautifulSoup(response.text, "html.parser")
            # Check if end is here
            parsed = urlparse.urlparse(response.url)
            page = int(urlparse.parse_qs(parsed.query)['page'][0])
            if page != page_num:
                work_flag = False
                logging.debug("scraper:scrape_country_decade_genre: finishing scrape response status: " +
                              str(response.status_code) + ", on url: " + url)
            # Get side filter menu
            html_tree = html_tree.find("div", {"id": "search_results"})
            # Get genre part of filter menu
            html_tree = html_tree.find_all('a', {"class": "search_result_title"}, href=True)
            albums = []
            # Get genre from every genre part
            for item in html_tree:
                albums.append(item['href'])
            logging.debug("scraper:scrape_country_decade_genre: albums found: country: " + country + ", decade: "
                          + decade + ", albums: " + str(albums))
            for item in albums:
                item_id = item.split("/")
                item_id = item_id[len(item_id) - 2] + "/" + item_id[len(item_id) - 1]

                query = """SELECT album.name FROM album WHERE album.site_id = :id_curr"""
                par_arr = {"id_curr": item_id}
                if not db.check_if_exists_in_db(query, par_arr):
                    time1 = time.time()
                    status, scrape_artist_num = scrape_album(BASE_URL + item, country, decade)
                    time2 = time.time()
                    if status:
                        album_counter += 1
                        logging.info("Country: " + country + ", decade: " +
                                     str(decade) + ", genre: " + str(genre) + ", album number: "
                                     + str(album_counter) + ", artist scraped: "
                                     + str(scrape_artist_num) + ", time: " + "{0:.2f}".format(time2 - time1)
                                     + "s , url: " + BASE_URL + item)
                    else:
                        logging.error("Country: " + country + ", decade: " + str(decade) +
                                      ", genre: " + str(genre) + ", album not scraped, url: " + BASE_URL + item)
        else:
            # If flag is out of bound it means it has finished all pages for current filters
            logging.debug("scraper:scrape_country_decade_genre: finishing scrape response status: " +
                          str(response.status_code) + ", on url: " + url)
            work_flag = False
    return album_counter


def scrape_album(url, country, decade):
    scrape_artist_num = 0
    response = requests.get(url)
    if response.status_code == REQUEST_STATUS_OK:
        # Create html_tree of all page
        html_tree = BeautifulSoup(response.text, "html.parser")
        # Get album id
        album_site_id = response.url.split("/")
        album_site_id = album_site_id[len(album_site_id) - 2] + "/" + album_site_id[len(album_site_id) - 1]
        # Create artist id rate set
        artist_rate_set = set()
        # Get title header of album
        title_tree = html_tree.find("h1", {"id": "profile_title"})
        # Get artist of album
        album_artist_tree = title_tree.find('a', href=re.compile("artist"))
        album_artist_url = album_artist_tree['href']
        album_artist_id = album_artist_url.split("/")
        album_artist_id = album_artist_id[len(album_artist_id) - 1]
        album_artist_id = album_artist_id.split("-")
        album_artist_id = album_artist_id[0]
        artist_rate_set.add(album_artist_id)
        # Get title of album
        album_title_tree = title_tree.find_all("span")
        album_title = album_title_tree[2].text
        album_title = album_title.strip()
        # Get album styles
        style_tree = html_tree.find_all('a', href=re.compile("/style/"))
        styles = []
        for item in style_tree:
            styles.append(item.string)
        # Get album genres
        genre_tree = html_tree.find_all('a', href=re.compile("/genre/"))
        genres = []
        for item in genre_tree:
            genres.append(item.string)
        # Get album year
        year_tree = html_tree.find('a', href=re.compile("year"))
        year = None
        if year_tree:
            year = year_tree.string
            year = year.strip().split(" ")
            year = year[len(year) - 1]
            year = int(year)
        # Get album formats
        format_tree = html_tree.find_all('a', href=re.compile("format_exact"))
        formats = []
        for item in format_tree:
            formats.append(item.string)
            other_elems = item.next_sibling.strip().split(",")
            for item_2 in other_elems:
                if item_2 != '':
                    formats.append(item_2.strip())
        # Get album rating
        rating_tree = html_tree.find("span", {"class": "rating_value"})
        rating = None
        try:
            rating = float(rating_tree.string)
        except:
            pass

        logging.debug("Album info[album_site_id: " + str(album_site_id) + ", artist_url: " + album_artist_url +
                      ", album_title: " + album_title + ", genres: " + str(genres) + ", styles: " + str(styles)
                      + ", rating: " + str(rating) + ", country: " + country + ", decade: " + decade + ", formats: "
                      + str(formats) + ", year: " + str(year) + "]")

        # Get songs of album
        songs = []
        songs_tree = html_tree.find('div', {"id": "tracklist"})
        if songs_tree:
            songs_tree = songs_tree.find_all('tr')
            for item in songs_tree:
                song_name_tree = item.find('a', href=re.compile("track"))
                if not song_name_tree:
                    continue
                song_name = song_name_tree.find('span', {"class": "tracklist_track_title"}).string
                song_url = song_name_tree['href']
                song_id = song_url.split("/")
                song_id = song_id[len(song_id) - 1]
                # Find duration of song
                song_duration = None
                song_duration_tree = item.find('td', {'class': 'tracklist_track_duration'})
                if song_duration_tree:
                    song_duration_tree = song_duration_tree.find('span')
                    song_duration = song_duration_tree.string
                    if song_duration:
                        duration_parts = song_duration.split(":")
                        song_duration = int(duration_parts[0]) * 60 + int(duration_parts[1])
                # Extra artists
                artists = []
                artists_tree = item.find_all('span', {'class': 'tracklist_extra_artist_span'})
                for item_2 in artists_tree:
                    artist_name_tree = item_2.find('a', href=True)
                    if not artist_name_tree:
                        continue
                    artist_name = artist_name_tree.string
                    artist_url = artist_name_tree['href']
                    artist_id = artist_url.split("/")
                    artist_id = artist_id[len(artist_id) - 1].split("-")
                    artist_id = artist_id[0]
                    artist_rate_set.add(artist_id)
                    # Get artists doing in song
                    artists_item = item_2.next
                    artist_parts = []
                    if artists_item:
                        artists_item = artists_item.lower()
                        artists_item = artists_item.split(" – ")[0]
                        artists_item = artists_item.split(", ")
                        if "music by" in artists_item:
                            artist_parts.append("music")
                        if "lyrics by" in artists_item:
                            artist_parts.append("lyrics")
                        if "arranged by" in artists_item:
                            artist_parts.append("arranged")
                        if "vocals" in artists_item:
                            artist_parts.append("vocals")
                    if len(artist_parts) > 0:
                        artists.append({"name": artist_name, "url": artist_url, "id": artist_id, "part": artist_parts})
                songs.append({"name": song_name, "url": song_url,
                              "duration": song_duration, "id": song_id, "parts": artists})

        logging.debug("Album songs: " + str(songs))

        # Get versions of same album
        versions = []
        versions_tree = html_tree.find('table', {"id": "versions"})
        if versions_tree:
            versions_tree = versions_tree.find_all('td', {"class": "title"})
            for item in versions_tree:
                item = item.find('a', href=True)
                version = item.string
                version_url = item['href']
                version_id = item['href'].split("/")
                version_id = version_id[len(version_id) - 2] + "/" + version_id[len(version_id) - 1]
                versions.append({"name": version, "url": version_url, "id": version_id})

        logging.debug("Album versions: " + str(versions))

        # Get artists from other credits
        credits_tree = html_tree.find('div', {'id': 'credits'})
        artist_specific_credits = []
        if credits_tree:
            credits_tree = credits_tree.find_all('li')
            for item in credits_tree:
                artist_part_temp = item.find('span').string
                artist_part_temp = artist_part_temp.lower()
                artists_temp = []
                artists_temp_tree = item.find_all('a', href=re.compile("artist"))
                for item_2 in artists_temp_tree:
                    temp_id = item_2['href']
                    temp_id = temp_id.split("/")
                    temp_id = temp_id[len(temp_id) - 1]
                    temp_id = temp_id.split("-")
                    temp_id = temp_id[0]
                    artists_temp.append({"url": item_2['href'], "id": temp_id})
                    artist_rate_set.add(temp_id)
                if "music by" in artist_part_temp:
                    artist_specific_credits.append({"type": "music", "artists": artists_temp})
                if "lyrics by" in artist_part_temp:
                    artist_specific_credits.append({"type": "lyrics", "artists": artists_temp})
                if "arranged by" in artist_part_temp:
                    artist_specific_credits.append({"type": "arranged", "artists": artists_temp})
                if "vocals" in artist_part_temp:
                    artist_specific_credits.append({"type": "vocals", "artists": artists_temp})

        logging.debug("Album credits: " + str(artist_specific_credits))
        logging.debug("All artists: " + str(artist_rate_set))

        # DB Manipulations
        # Get album id, if it doesn't exist create it
        album_group_id = None
        for item in versions:
            query = """SELECT album.id_album_group FROM album WHERE album.site_id = :id_curr"""
            par_arr = {"id_curr": item["id"]}
            db_album = db.check_if_exists_in_db(query, par_arr)
            if db_album:
                album_group_id = db_album['id_album_group']
                break
        if not album_group_id:
            query = """INSERT INTO album_group DEFAULT VALUES RETURNING id as id"""
            album_group_id = db.insert_in_db(query, None)
        # Add album to db
        create_params = {
            "site_id": album_site_id,
            "group_id": album_group_id,
            "rating": rating,
            "year": year,
            "decade": int(decade),
            "country": country,
            "name": album_title,
            "is_cyrillic": not only_roman_chars(album_title)
        }
        query = """INSERT INTO album(site_id, id_album_group, rating, year, decade, country, name, is_cyrillic)
         VALUES(:site_id, :group_id, :rating, :year, :decade, :country, :name, :is_cyrillic) RETURNING id as id"""
        album_id = db.insert_in_db(query, create_params)
        if not album_id:
            logging.error("scraper:scrape_album: album not added to db, album: " + str(create_params))
            return False
        # Add genres to db
        query = """INSERT INTO album_genre(content, id_album) VALUES(:content, :album_id) RETURNING id as id"""
        for item in genres:
            params = {
                "content": item,
                "album_id": album_id
            }
            gen_id = db.insert_in_db(query, params)
            if not gen_id:
                logging.error("scraper:scrape_album: genre not added to db, album: " + str(create_params)
                              + ", genre: " + item)
        # Add styles to db
        query = """INSERT INTO album_style(content, id_album) VALUES(:content, :album_id) RETURNING id as id"""
        for item in styles:
            params = {
                "content": item,
                "album_id": album_id
            }
            gen_id = db.insert_in_db(query, params)
            if not gen_id:
                logging.error("scraper:scrape_album: style not added to db, album: " + str(create_params)
                              + ", style: " + item)
        # Add formats to db
        query = """INSERT INTO album_format(content, id_album) VALUES(:content, :album_id) RETURNING id as id"""
        for item in formats:
            params = {
                "content": item,
                "album_id": album_id
            }
            gen_id = db.insert_in_db(query, params)
            if not gen_id:
                logging.error("scraper:scrape_album: format not added to db, album: " + str(create_params)
                              + ", format: " + item)
        # Add songs and their relation with album and artists to db
        query_song_select = """SELECT song.id FROM song WHERE song.site_id = :id_curr"""
        query_song = """INSERT INTO song(duration, name, site_id) VALUES(:duration, :name, :web) RETURNING id as id"""
        query_relation = """INSERT INTO song_on_album(id_album, id_song) VALUES(:id_a, :id_s) RETURNING id as id"""
        query_artist_select = "SELECT artist.id FROM artist WHERE artist.site_id = :id_curr"
        query_artist_relation = "INSERT INTO artist_on_song(id_artist, id_song, type) " \
                                "VALUES(:id_a, :id_s, :type) RETURNING id as id"
        for item in songs:
            par_arr = {"id_curr": item["id"]}
            db_album = db.check_if_exists_in_db(query_song_select, par_arr)
            if db_album:
                song_id = db_album['id']
            else:
                song_params = {
                    "duration": item["duration"],
                    "name": item["name"],
                    "web": item["id"]
                }
                song_id = db.insert_in_db(query_song, song_params)
                if not song_id:
                    logging.error("scraper:scrape_album: song not added to db, album: " + str(create_params)
                                  + ", song: " + str(item))
                    continue
            relation_params = {
                "id_a": album_id,
                "id_s": song_id
            }
            gen_val = db.insert_in_db(query_relation, relation_params)
            if not gen_val:
                logging.error("scraper:scrape_album: relation song album not added to db, album: " + str(create_params)
                              + ", song: " + str(item))
            for item_2 in item["parts"]:
                parts_params = {
                    "id_curr": item_2["id"]
                }
                db_artist = db.check_if_exists_in_db(query_artist_select, parts_params)
                if db_artist:
                    artist_id = db_artist['id']
                else:
                    artist_id = scrape_artist(BASE_URL + item_2["url"])
                if artist_id:
                    for part in item_2["part"]:
                        relation_params = {
                            "id_a": artist_id,
                            "id_s": song_id,
                            "type": part
                        }
                        gen_val = db.insert_in_db(query_artist_relation, relation_params)
                        if not gen_val:
                            logging.error(
                                "scraper:scrape_album: relation song artist not added to db, album: "
                                + str(create_params) + ", artist: " + str(item_2) + ", part: " + part)
        # Add ratings, relation artist with album to db
        query_artist_select = "SELECT artist.id FROM artist WHERE artist.site_id = :id_curr"
        query_artist_relation = "INSERT INTO artist_rating(id_artist, id_album) " \
                                "VALUES(:id_artist, :id_album) RETURNING id as id"
        for item in artist_rate_set:
            parts_params = {
                "id_curr": item
            }
            db_artist = db.check_if_exists_in_db(query_artist_select, parts_params)
            if db_artist:
                artist_id = db_artist['id']
            else:
                artist_id = scrape_artist(BASE_URL + "/artist/" + item)
                if artist_id:
                    scrape_artist_num += 1
            if artist_id:
                relation_params = {
                    "id_artist": artist_id,
                    "id_album": album_id,
                }
                gen_val = db.insert_in_db(query_artist_relation, relation_params)
                if not gen_val:
                    logging.error(
                        "scraper:scrape_album: relation album artist rating not added to db, album: "
                        + str(create_params) + ", artist id: " + str(item))
    else:
        logging.debug("scraper:scrape_album: finishing scrape response status: " +
                      str(response.status_code) + ", on url: " + url)
        return False, scrape_artist_num
    return True, scrape_artist_num


# Scrape group or person for artist details
def scrape_artist(url):
    response = requests.get(url)
    if response.status_code == REQUEST_STATUS_OK:
        # Create html_tree of all artist page
        html_tree = BeautifulSoup(response.text, "html.parser")

        # Get album id
        artist_site_id = response.url.split("/")
        artist_site_id = artist_site_id[len(artist_site_id) - 1]
        artist_site_id = artist_site_id.split("-")
        artist_site_id = artist_site_id[0]

        # Find artist name
        artist_name = None
        artist_name_tree = html_tree.find('h1', {'class': 'hide_mobile'})
        if artist_name_tree:
            artist_name = artist_name_tree.string

        # Return if there is no name and log it
        if not artist_name:
            logging.error("scraper:scrape_artist: artist does not have name, on url: " + url)
            return None

        # Find vocals num
        vocals_num = None
        vocals_html_tree = html_tree.find('a', {'data-credit-subtype': 'Vocals'})
        if vocals_html_tree:
            vocals_html_tree = vocals_html_tree.find('span', {'class': 'facet_count'})
            vocals_num = vocals_html_tree.string

        # Check if group (if it has members)
        is_group_tree = html_tree.find_all('div', {'class': 'head'})
        is_group = False
        for item in is_group_tree:
            if item.string == "Members:":
                is_group = True
                break

        # Find sites
        sites = []
        sites_tree = html_tree.find_all('a', {'rel': 'nofollow'}, href=True)
        for item in sites_tree:
            sites.append(item['href'])

        logging.debug("Artist info[name: " + artist_name + " , is_group: " + str(is_group) + " , id: "
                      + artist_site_id + " , vocal num: " + str(vocals_num) + " , sites: " + str(sites) + "]")

        # DB Manipulations
        # Insert artist into db
        query = """INSERT INTO artist(site_id, is_group, vocals, name) VALUES
        (:site_id, :is_group, :vocals, :name) RETURNING id as id"""
        params = {
            "site_id": artist_site_id,
            "is_group": is_group,
            "vocals": vocals_num,
            "name": artist_name
        }
        artist_id = db.insert_in_db(query, params)
        if not artist_id:
            logging.error("scraper:scrape_artist: artist not added to db, artist: " + artist_name
                          + ", site_id: " + artist_site_id)
            return None
        # Add sites to DB
        query = """INSERT INTO artist_web(id_artist, web) VALUES
                (:id_artist, :web) RETURNING id as id"""
        for item in sites:
            params = {
                "id_artist": artist_id,
                "web": item
            }
            gen_id = db.insert_in_db(query, params)
            if not gen_id:
                logging.error("scraper:scrape_artist: site for artist not added to db, artist: " + artist_name
                              + ", site: " + item)
        return artist_id
    else:
        logging.error("scraper:scrape_artist: response status: " + str(response.status_code) + ", on url: " + url)
        return None


scrape_country("Yugoslavia")
# scrape_album(
#    'https://www.discogs.com/%D0%91%D0%B0j%D0%B0%D0%B3%D0%B0-%D0%98%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80%D0%B8-%D0%94%D0%B0%D1%99%D0%B8%D0%BD%D0%B0-%D0%94%D0%B8%D0%BC-%D0%9F%D1%80%D0%B0%D1%88%D0%B8%D0%BD%D0%B0/master/712784',
#    'Yugoslavia', "1980")
# scrape_artist('https://www.discogs.com/artist/504779-Mom%C4%8Dilo-Bajagi%C4%87')
# scrape_artist('https://www.discogs.com/artist/525165-Bajaga-I-Instruktori')
