from bs4 import BeautifulSoup
import requests
import logging
import re

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
            decades.append(int(item.find("small").next.next))
        logging.debug("Decades: " + str(decades))
    else:
        logging.error("scraper:scrape_country: response status: " + str(response.status_code) + ", on url: " + url)


# Gets all data for one country, for one specific decade
def scrape_country_decade(country, decade):
    pass


scrape_country("Yugoslavia")