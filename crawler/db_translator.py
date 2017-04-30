import sqlalchemy
from sqlalchemy import create_engine, select, insert, MetaData, Table

class Translator():
    def __init__(self, db = 'postgresql://localhost/beetle_crawler_development'):
        self.database_engine = create_engine(db)
        self.connection = self.database_engine.connect()
        metadata = MetaData()
        self.weburls = Table('weburls', metadata, autoload = True, autoload_with = self.database_engine)
        self.weburlsandcontent = Table('weburlsandcontent', metadata, autoload = True, autoload_with = self.database_engine)
        self.current_id = 1

    def write_url(self, url):
        statement = insert(self.weburls).values(weburl = url)
        self.connection.execute(statement)

    def write_urls_and_content(self, url, title, description, keywords):
        statement = insert(self.weburlsandcontent).values(weburl = url, title = title, description = description, keywords = keywords)
        self.connection.execute(statement)
        self.current_id += 1

    def prepare_urls_for_writing_to_db(self, weburls):
        for url in weburls:
            if self.get_weburls_table_size() < 1000:
                self.write_url(url)
            else:
                raise Exception

    def get_weburls_table_size(self):
        select_all = select([self.weburls])
        return self.connection.execute(select_all).rowcount

    def get_next_url(self):
        my_url = select([self.weburls]).where(self.weburls.c.id == self.current_id)
        result_proxy = self.connection.execute(my_url)
        return result_proxy.fetchone()['weburl']
