"""
1. check allowed domain
2. check duplicate urls
"""
import time
import hashlib
from pathlib import Path
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

import requests


class Crawler:
    def __init__(self, start_url, allowed_domain, cache=True, cache_dir=None):
        self._start_url = start_url
        self._allowed_domain = allowed_domain.replace("www.", "")
        self._cache = cache
        self._cache_dir = Path(cache_dir or "cache")

        # stats
        self._not_allowed_domains_count = 0
        self._not_allowed_domains = set()
        self._duplicate_urls_count = 0
        self._crawled_urls = set()

    def crawl(self):
        print("Crawling started")
        print(f"Start url - {self._start_url}")
        start = time.time()
        self.__crawl_url(self._start_url)
        end = time.time()
        print(f"Crawled pages count - {len(self._crawled_urls)}")
        print(f"Duplicate urls - {self._duplicate_urls_count}")
        print(f"Not allowed domains - {self._not_allowed_domains}")
        print(f"Time elapsed - {end-start}")

    def __crawl_url(self, url):
        domain = urlparse(url).netloc.replace("www.", "")
        if domain != self._allowed_domain:
            print(f"Skipping not allowed domain - {url}")
            self._not_allowed_domains_count += 1
            self._not_allowed_domains.add(domain)
            return
        if url in self._crawled_urls:
            print(f"Skipping duplicate url - {url}")
            self._duplicate_urls_count += 1
            return
        self._crawled_urls.add(url)

        if self._cache:
            url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
            cache_file_path = self._cache_dir / url_hash
            if cache_file_path.exists():
                html_text = cache_file_path.open(mode="r").read()
            else:
                response = requests.get(url)
                html_text = response.text
                cache_file_path.open(mode="w").write(html_text)
        else:
            response = requests.get(url)
            html_text = response.text

        next_urls = self.__extract_urls(url, html_text)
        for next_url in next_urls:
            self.__crawl_url(next_url)

    def __extract_urls(self, base_url, html_text):
        html_tree = BeautifulSoup(html_text, "html.parser")
        a_tags = html_tree.find_all("a")
        result = []
        for a_tag in a_tags:
            href = a_tag.attrs.get("href", None)
            if href:
                new_url = urljoin(base_url, href)
                if new_url in self._crawled_urls:
                    self._duplicate_urls_count += 1
                else:
                    result.append(new_url)
        return result


if __name__ == '__main__':
    start_url = "http://quotes.toscrape.com/"
    crawler = Crawler(start_url, "quotes.toscrape.com")
    crawler.crawl()

