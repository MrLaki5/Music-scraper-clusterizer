from bs4 import BeautifulSoup
import requests
import logging
import re
import urllib.parse as urlparse

# Logger configuration
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Logger started!")

REQUEST_STATUS_OK = 200

BASE_URL = "https://www.discogs.com/search/"
FAST_LAYOUT_ATTR = "layout=sm"
GENRE_ATTR = "genre_exact="
DECADE_ATTR = "decade="
COUNTRY_ATTR = "country_exact="
PAGE_NUM_ATTR = "page="
LIMIT_MAX_ATTR = "limit=250"


# Gets all data for one country, iterating through decades and genre
def scrape_country(country):
    url = BASE_URL + "?" + COUNTRY_ATTR + country + "&" + FAST_LAYOUT_ATTR
    response = requests.get(url)
    if response.status_code == REQUEST_STATUS_OK:
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
            scrape_country_decade(country, item)
    else:
        logging.error("scraper:scrape_country: response status: " + str(response.status_code) + ", on url: " + url)


# Gets all data for one country, for one specific decade
def scrape_country_decade(country, decade):
    url = BASE_URL + "?" + COUNTRY_ATTR + country + "&" + DECADE_ATTR + decade + "&" + FAST_LAYOUT_ATTR
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
                scrape_country_decade_genre(country, decade, item)
        else:
            logging.debug("scraper:scrape_country_decade: no genres found: country: " + country + ", decade: " + decade)
            scrape_country_decade_genre(country, decade)
    else:
        logging.error("scraper:scrape_country_decade: response status: " +
                      str(response.status_code) + ", on url: " + url)


# Gets all data for one country, for one specific decade, for one specific genre
def scrape_country_decade_genre(country, decade, genre=None):
    work_flag = True
    page_num = 0
    while work_flag:
        page_num += 1
        # Build url
        url = (BASE_URL + "?" + COUNTRY_ATTR + country + "&" + DECADE_ATTR + decade + "&" +
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
        else:
            # If flag is out of bound it means it has finished all pages for current filters
            logging.debug("scraper:scrape_country_decade_genre: finishing scrape response status: " +
                          str(response.status_code) + ", on url: " + url)
            work_flag = False


scrape_country("Yugoslavia")