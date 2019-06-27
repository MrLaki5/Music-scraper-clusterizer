import threading
import scraper
import logging
import time


class ScrapePool:

    def __init__(self, thread_num):
        self.thread_num = thread_num
        self.threads = []
        self.album_counter = 0
        self.album_counter_lock = threading.Lock()
        self.thread_sem = threading.Semaphore(value=thread_num)
        i = 0
        while i < self.thread_num:
            self.threads.append(ScrapeThread(self))
            i += 1
        for worker in self.threads:
            worker.start()

    def put_job(self, url, country, decade, genre):
        self.thread_sem.acquire(blocking=True)
        for item in self.threads:
            with item.lock:
                if not item.is_working:
                    item.put_job(url, country, decade, genre)
                    break

    def increment_album_cnt(self):
        with self.album_counter_lock:
            self.album_counter += 1
            curr_cnt = self.album_counter
        return curr_cnt

    def interrupt_pool(self):
        for item in self.threads:
            with item.lock:
                item.is_interrupted = True
                item.event.set()
            try:
                item.join()
            except Exception as ex:
                pass


class ScrapeThread(threading.Thread):

    def __init__(self, owner):
        super(ScrapeThread, self).__init__()
        self.lock = threading.Lock()
        self.is_working = False
        self.data_url = None
        self.data_country = None
        self.data_decade = None
        self.data_genre = None
        self.is_interrupted = False
        self.event = threading.Event()
        self.owner = owner

    def put_job(self, url, country, decade, genre):
        self.data_url = url
        self.data_country = country
        self.data_decade = decade
        self.data_genre = genre
        self.is_working = True
        self.event.set()

    def run(self):
        while True:
            self.event.wait()
            with self.lock:
                self.event.clear()
                if self.is_interrupted:
                    break
            time1 = time.time()
            status, scrape_artist_num = scraper.scrape_album(self.data_url, self.data_country, self.data_country)
            time2 = time.time()
            album_counter = self.owner.increment_album_cnt()
            if status:
                album_counter += 1
                logging.info("Country: " + self.data_country + ", decade: " +
                             str(self.data_decade) + ", genre: " + str(self.data_genre) + ", album number: "
                             + str(album_counter) + ", artist scraped: "
                             + str(scrape_artist_num) + ", time: " + "{0:.2f}".format(time2 - time1)
                             + "s, url: " + self.data_url)
            else:
                logging.error("Country: " + self.data_country + ", decade: " + str(self.data_decade) +
                              ", genre: " + str(self.data_genre) + ", album not scraped, url: " + self.data_url)
            with self.lock:
                self.is_working = False
            self.owner.thread_sem.release()
