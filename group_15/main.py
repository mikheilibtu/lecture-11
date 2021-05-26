"""
1. check allowed domain
2. check duplicate urls
"""
import hashlib
import time
from pathlib import Path
from urllib import parse

import requests
from bs4 import BeautifulSoup


class WebsiteCrawler:

    def __init__(self, url, allowed_domain, enable_cache=True, cache_dir="cache"):
        self._url = url
        self._allowed_domain = allowed_domain.replace("www.", "")
        self._enable_cache = enable_cache
        self._cache_dir = Path(cache_dir)

        if not self._cache_dir.exists():
            self._cache_dir.mkdir()

        self._crawled_urls = set()
        self._duplicate_urls_count = 0

        self._not_allowed_domains = set()

    def __extract_urls(self, html_text, url):
        result = []
        html_tree = BeautifulSoup(html_text, "html.parser")
        a_tags = html_tree.find_all("a")
        for a_tag in a_tags:
            href = a_tag.attrs.get("href", None)
            if href:
                new_url = parse.urljoin(url, href)
                if new_url in self._crawled_urls:
                    self._duplicate_urls_count += 1
                else:
                    result.append(new_url)
        return result

    def __crawl_url(self, url):
        domain = parse.urlparse(url).netloc
        domain.replace("www.", "")
        if domain != self._allowed_domain:
            print(f"Not allowed domain found - {domain}")
            self._not_allowed_domains.add(domain)
            return
        if url in self._crawled_urls:
            print(f"Found duplicate url - {url}")
            self._duplicate_urls_count += 1
            return
        self._crawled_urls.add(url)

        if self._enable_cache:
            url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
            file_path = self._cache_dir / url_hash
            if file_path.exists():
                html_text = file_path.open("r").read()
            else:
                response = requests.get(url)
                html_text = response.text
                file_path.open("w").write(html_text)
        else:
            response = requests.get(url)
            html_text = response.text

        new_urls = self.__extract_urls(html_text, url)
        for new_url in new_urls:
            self.__crawl_url(new_url)

    def start_crawling(self):
        start = time.time()
        print("Crawling started")
        print(f"Start url - {self._url}")
        print(f"Caching is enabled - {self._enable_cache}")
        self.__crawl_url(self._url)
        end = time.time()

        print("Crawling finished")
        print("Spent time - {:.6f} s".format(end - start))
        print(f"Crawled urls - {len(self._crawled_urls)}")
        print(f"Duplicate urls - {self._duplicate_urls_count}")
        print(f"Not allowed domains urls - {self._not_allowed_domains}")


if __name__ == '__main__':
    web_crawler = WebsiteCrawler("http://quotes.toscrape.com/", "quotes.toscrape.com", True, "cache")
    web_crawler.start_crawling()
