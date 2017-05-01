import unittest
from mock import Mock
from mock import MagicMock
from crawler.crawler import Crawler
from bs4 import BeautifulSoup
import os

class TestingCrawler(unittest.TestCase):

    def setUp(self):
        self.translator = MagicMock()
        self.translator.get_weburls_table_size = MagicMock(return_value=50)
        self.translator.get_weburls_and_content_table_size = MagicMock(return_value=10)
        self.translator.get_next_url = MagicMock(return_value='http://www.exampletest.com')
        self.translator.database_limit = 10
        self.crawler = Crawler(self.translator)
        self.local_html_file = "file://" + (os.path.abspath("spec/website/index.html"))
        self.crawler.crawl(self.local_html_file)


    def test_crawler_is_instance_of_Crawler(self):
        self.assertIsInstance(self.crawler, Crawler)

    def test_crawl_calls_translator_write_url(self):
        self.translator.write_url = MagicMock()
        self.crawler.crawl(self.local_html_file)
        self.translator.write_url.assert_called_once_with(self.local_html_file)

    def test_crawl_accepts_and_assigns_url(self):
        self.assertEqual(self.crawler.url, self.local_html_file)


    def test_return_all_content_assigns_title(self):
        self.crawler.return_all_content()
        self.assertIn("Cats and Dogs", self.crawler.webpage_title)

    def test_return_all_content_assigns_description(self):
        self.crawler.return_all_content()
        self.assertIn("Page about cats and dogs", self.crawler.webpage_description)

    def test_return_all_content_assigns_keywords(self):
        self.crawler.return_all_content()
        self.assertIn("cats,dogs", self.crawler.webpage_keywords)

    def test_return_all_content_calls_translator_write_urls_and_content(self):
        self.translator.write_urls_and_content = MagicMock()
        self.crawler.return_all_content()
        self.translator.write_urls_and_content.assert_called_once_with(self.local_html_file, "Cats and Dogs", "Page about cats and dogs", "cats,dogs")

    def test_return_all_content_calls_crawl_next_url(self):
        self.crawler.crawl_next_url = MagicMock()
        self.crawler.return_all_content()
        self.crawler.crawl_next_url.assert_called_once()


    def test_save_found_weburls_saves_all_urls_from_webpage_in_an_array(self):
        test_soup = BeautifulSoup('<!DOCTYPE html>\n<html>\n\n<head>\n <title>Cats and Dogs</title>\n</head><body><a href="www.dogs.com">Dogs</a><a href="www.cats.com">Cats</a></body></html>', 'html.parser')
        self.crawler.save_found_weburls(test_soup)
        self.assertIn("www.dogs.com", self.crawler.webpage_urls)
        self.assertIn("www.cats.com", self.crawler.webpage_urls)

    def test_save_found_weburls_calls_translator_prepare_urls_for_writing_to_db(self):
        self.translator.prepare_urls_for_writing_to_db = MagicMock()
        test_soup = BeautifulSoup('<!DOCTYPE html>\n<html>\n\n<head>\n <title>Cats and Dogs</title>\n</head><body><a href="www.dogs.com">Dogs</a><a href="www.cats.com">Cats</a></body></html>', 'html.parser')
        self.crawler.save_found_weburls(test_soup)
        test_urls_array = ["www.dogs.com", "www.cats.com"]
        self.translator.prepare_urls_for_writing_to_db.assert_called_once_with(test_urls_array)

    def test_save_found_weburls_does_not_save_title(self):
        test_soup = BeautifulSoup('<!DOCTYPE html>\n<html>\n\n<head>\n <title>Cats and Dogs</title>\n</head><body><a href="www.dogs.com">Dogs</a><a href="www.cats.com">Cats</a></body></html>', 'html.parser')
        self.crawler.save_found_weburls(test_soup)
        test_title = test_soup.title.string
        self.assertNotIn(test_title, self.crawler.webpage_urls)


    def test_crawl_next_url_calls_translator_get_next_url(self):
        self.translator.get_next_url = MagicMock()
        self.crawler.crawl_next_url()
        self.translator.get_next_url.assert_called_once()

    def test_crawl_next_url_will_not_crawl_when_both_tables_are_full(self):
        self.translator.get_weburls_table_size = MagicMock(return_value=1000)
        self.translator.get_weburls_and_content_table_size = MagicMock(return_value=1000)
        self.assertEqual(self.crawler.crawl_next_url(), 'The databases are full')
