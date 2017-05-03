import urllib.request
import sys
import os
from bs4 import BeautifulSoup
from db_translator import Translator


class Crawler():
    def __init__(self, translator = Translator()):
        sys.setrecursionlimit(15000)
        self.translator = translator

    def crawl(self, url):
        self.url = url
        try:
            self.page = urllib.request.urlopen(url).read()
            self.translator.write_url(url)
            self.return_all_content()
        except:
            self.crawl_next_url()

    def return_all_content(self):
        soup = BeautifulSoup(self.page, "html.parser", from_encoding="UTF-8")
        self.save_found_weburls(soup)
        self.webpage_title = self.find_webpage_title(soup)
        self.webpage_description = self.find_webpage_metadata(soup, 'description')
        self.webpage_keywords = self.find_webpage_metadata(soup, 'keywords')
        print(self.webpage_title)
        print(self.webpage_description)
        print(self.webpage_keywords)
        if self.empty_titles_and_descriptions(self.webpage_title, self.webpage_description):
            self.crawl_next_url()
        else:
            self.translator.write_urls_and_content(self.url, self.webpage_title, self.webpage_description, self.webpage_keywords)
            self.crawl_next_url()

    def empty_titles_and_descriptions(self, title, description):
        return title == "" and description == ""

    def save_found_weburls(self, soup):
        self.webpage_urls = []
        for link in soup.find_all('a', href=True):
            self.webpage_urls.append(link['href'])
        self.translator.prepare_urls_for_writing_to_db(self.webpage_urls)

    def crawl_next_url(self):
        next_url_to_crawl = self.translator.get_next_url()
        print("NEXT URL TO CRAWL: ", next_url_to_crawl)
        if self.translator.both_tables_are_not_full_yet():
            if next_url_to_crawl != None:
                self.crawl(next_url_to_crawl)
        else:
            print(self.translator.full_database_message())

    def find_webpage_title(self, soup):
        return soup.title.string if soup.title else ''

    def find_webpage_metadata(self, soup, name):
        try:
            return soup.find("meta", {"name": name})['content']
        except:
            return ''

sites_to_crawl = "file://" + os.path.abspath("sites_to_crawl.html")
# print(sites_to_crawl)

crawler = Crawler()
crawler.crawl(sites_to_crawl)
