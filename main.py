import hashlib
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup


class Crawler:

    def __init__(self, url, allowed_domain, cache=True, cache_dir=None, print_stats=True):
        self._url = url
        self._allowed_domain = allowed_domain
        self._print_stats = print_stats
        self._cache = cache
        self._cache_dir = Path(cache_dir or "cache")
        self._crawled_urls = set()
        self._not_allowed_urls = set()
        self._duplicates_counter = 0
        self._not_allowed_counter = 0

    def start_crawling(self):
        print("Crawling started")
        print(f"Start URL = {self._url}")
        self.__crawl_page(self._url)
        print(f"Scrapped pages - {len(self._crawled_urls)}")
        print(f"Duplicate urls - {self._duplicates_counter}")
        print(f"Not allowed domains - {self._not_allowed_urls}")
        print(f"Not allowed domains count - {self._not_allowed_counter}")

    def __crawl_page(self, url):
        domain = urlparse(url).netloc.replace("www.", "")
        if url in self._crawled_urls:
            print(f"Skip duplicate url - {url}")
            self._duplicates_counter += 1
            return None
        elif domain != self._allowed_domain:
            print(f"Skip not allowed domain - {url}")
            self._not_allowed_counter += 1
            if domain not in self._not_allowed_urls:
                self._not_allowed_urls.add(domain)
            return None
        self._crawled_urls.add(url)
        print(f"Processing - {url}")
        if self._cache:
            url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
            file_path = self._cache_dir / url_hash
            if file_path.exists():
                html_text = file_path.open(mode="r").read()
            else:
                response = requests.get(url)
                html_text = response.text
                file_path.open(mode="w").write(html_text)
        else:
            response = requests.get(url)
            html_text = response.text

        next_urls = self._extract_urls_from_html(url, html_text)
        for next_url in next_urls:
            self.__crawl_page(next_url)

    def _extract_urls_from_html(self, request_url, html_text):
        html_tree = BeautifulSoup(html_text, "html.parser")
        a_tags = html_tree.find_all("a")
        result = []
        for a_tag in a_tags:
            href = a_tag.attrs.get("href")
            if href:
                url = urljoin(request_url, href)
                if url not in self._crawled_urls:
                    result.append(url)
                else:
                    self._duplicates_counter += 1
        return result


if __name__ == '__main__':
    import time
    start = time.time()
    crawler = Crawler("http://quotes.toscrape.com/", "quotes.toscrape.com", cache=True)
    crawler.start_crawling()
    end = time.time()
    print(f"Time elapsed - {end - start}")
