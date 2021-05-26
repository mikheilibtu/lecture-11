"""
1. check allowed domain
2. check duplicate urls
"""
import time
from urllib import parse

import requests
from bs4 import BeautifulSoup


class WebsiteCrawler:
    def __init__(self, url, allowed_domain):
        self._url = url
        self._allowed_domain = allowed_domain.replace("www.", "")

        self._crawled_urls = set()
        self._not_allowed_domains = set()

        self._duplicate_urls_counter = 0

    def __extract_urls(self, html_text, url):
        result = []
        html_tree = BeautifulSoup(html_text, "html.parser")
        a_tags = html_tree.find_all("a")

        for a_tag in a_tags:
            href = a_tag.attrs.get("href", None)
            if href:
                new_url = parse.urljoin(url, href)
                if new_url not in self._crawled_urls:
                    result.append(new_url)
                else:
                    self._duplicate_urls_counter += 1

        return result

    def __crawl_url(self, url):
        if url in self._crawled_urls:
            print(f"Found duplicate url - {url}")
            self._duplicate_urls_counter += 1
            return
        domain = parse.urlparse(url).netloc
        domain = domain.replace("www.", "")
        if domain != self._allowed_domain:
            print(f"Found duplicate domain - {domain}")
            self._not_allowed_domains.add(domain)
            return

        self._crawled_urls.add(url)
        response = requests.get(url)
        new_urls = self.__extract_urls(response.text, url)
        for new_url in new_urls:
            self.__crawl_url(new_url)

    def start_crawling(self):
        print("Crawling started")
        start_time = time.time()
        print(f"Start url - {self._url}")
        self.__crawl_url(self._url)

        print(f"Crawled urls - {len(self._crawled_urls)}")
        print(f"Duplicate urls - {self._duplicate_urls_counter}")
        print(f"Not allowed domains - {len(self._not_allowed_domains)}")

        end_time = time.time()
        print("Time spent - {:.6f}".format(end_time - start_time))


if __name__ == '__main__':
    start_url = "http://quotes.toscrape.com/"
    website_crawler = WebsiteCrawler(start_url, "quotes.toscrape.com")
    website_crawler.start_crawling()
