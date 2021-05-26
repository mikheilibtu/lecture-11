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
    def __init__(self, url, allowed_domain, caching_enabled=True, cache_dir="cache"):
        self._url = url
        self._allowed_domain = allowed_domain.replace("www.", "")
        self._caching_enabled = caching_enabled
        self._cache_dir = Path(cache_dir)

        if not self._cache_dir.exists():
            self._cache_dir.mkdir()

        self._scraped_urls = set()
        self._duplicate_url_counter = 0

        self._not_allowed_domains = set()

    def __extract_urls(self, html_text, base_url):
        result = []
        html_tree = BeautifulSoup(html_text, "html.parser")
        a_tags = html_tree.find_all("a")
        for a_tag in a_tags:
            href = a_tag.attrs.get("href", None)
            if href:
                new_url = parse.urljoin(base_url, href)
                if new_url in self._scraped_urls:
                    self._duplicate_url_counter += 1
                else:
                    result.append(new_url)

        return result

    def __crawl_url(self, url):
        domain = parse.urlparse(url).netloc
        domain.replace("www.", "")
        if domain != self._allowed_domain:
            print(f"Found not allowed domain - {domain}")
            self._not_allowed_domains.add(domain)
            return
        if url in self._scraped_urls:
            print(f"Found duplicate url - {url}")
            self._duplicate_url_counter += 1
            return
        self._scraped_urls.add(url)

        if self._caching_enabled:
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
        print("Crawling started")
        print(f"Start url - {self._url}")
        start = time.time()
        self.__crawl_url(self._url)
        end = time.time()

        print("Crawling finished")
        print("Crawling time - {:.6f}".format(end - start))
        print(f"Scraped urls count - {len(self._scraped_urls)}")
        print(f"Duplicate urls count - {self._duplicate_url_counter}")
        print(f"Not allowed domains - {self._not_allowed_domains}")


if __name__ == '__main__':
    my_crawler = WebsiteCrawler("http://quotes.toscrape.com/", "quotes.toscrape.com", True)
    my_crawler.start_crawling()
