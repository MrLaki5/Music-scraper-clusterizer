import time
import requests
from multiprocessing import Pool
import threading
from itertools import cycle
from lxml.html import fromstring


def get_proxies():
    url = 'https://www.sslproxies.org/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


site_num = 20
url = "https://www.discogs.com/%D0%91%D0%B0j%D0%B0%D0%B3%D0%B0-%D0%98%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80%D0%B8-%D0%94%D0%B0%D1%99%D0%B8%D0%BD%D0%B0-%D0%94%D0%B8%D0%BC-%D0%9F%D1%80%D0%B0%D1%88%D0%B8%D0%BD%D0%B0/master/712784"
process_num = 1
request_urls = []
for i in range(site_num):
    request_urls.append(url)


def something(x):
    results = requests.get(x[0], proxies={"http": x[1], "https": x[1]}, verify=False)
    # time.sleep(0.9)
    return results

class RequestHelper:
    def __init__(self, pool_size):
        self.pool = Pool(pool_size)

    def get_results(self, urls):
        proxies = get_proxies()
        proxy_pool = cycle(proxies)
        sleep_time = 0.9
        return_arr = []
        process_arr = urls
        print(str(process_arr))
        while True:
            proxy = next(proxy_pool)
            urls = process_arr
            process_arr = []
            for url in urls:
                process_arr.append([url, proxy])
            print(proxy)
            records = self.pool.map(something, process_arr)
            should_break = True
            process_arr = []
            print(str(records))
            for record in records:
                if record.status_code == 429:
                    should_break = False
                    print("Do again")
                    print(record.content)
                    process_arr.append(record.url)
                elif record.status_code == 200:
                    return_arr.append(record)
                    print("Done")
            if should_break:
                break
            else:
                time.sleep(sleep_time)
                sleep_time *= 2
        return return_arr


for i in range(1, 15):
    time1 = time.time()
    helper = RequestHelper(10)
    results = helper.get_results(request_urls)
    time2 = time.time()
    print(str(results))
    for item in results:
        print(item.status_code)
    print("{0:.2f}".format(time2 - time1))