import datetime
import sqlite3
import bs4
import lxml
import requests


class Crowler():
    def __init__(self, domain_name, pagination_address, item_link_selector):
        self.domain_name = domain_name
        self.pagination_address = pagination_address
        self.item_link_selector = item_link_selector

    def save_pages_to_sqlite(self, db_file_name, estimated_pages_count):
        page_url = self.domain_name + self.pagination_address
        connection = sqlite3.Connection(db_file_name)
        connection.execute("CREATE TABLE IF NOT EXISTS PAGES (ID INTEGER PRIMARY KEY AUTOINCREMENT, DATE DATETIME, NUM INT, URL NVARCHAR, CONTENT XML)")

        page_index = 1100
        while True:
            if (page_index > estimated_pages_count):
                break

            url = page_url.format(page_index)
            page_response = requests.get(url)
            
            dt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            connection.execute('''INSERT INTO PAGES (DATE, NUM, URL, CONTENT) VALUES(?, ?, ?, ?)''', (dt, page_index, url, page_response.content))

            print(url)
            page_index += 1

            if page_index % 100 == 0:
                connection.commit()

        connection.commit()
        connection.close()


    def save_items_to_sqlite(self, db_file_name):
        connection = sqlite3.Connection(db_file_name)
        connection.execute("CREATE TABLE IF NOT EXISTS ITEMS (ID INTEGER PRIMARY KEY AUTOINCREMENT, DATE DATETIME, PAGE_ID INT, URL NVARCHAR, CONTENT XML)")

        columns = connection.execute("PRAGMA TABLE_INFO(ITEMS)")
        if not len([column[1].lower() for column in columns if column[1].lower() == 'COMMENTS'.lower()]) > 0:
            connection.execute(f"ALTER TABLE ITEMS ADD COLUMN COMMENTS NVARCHAR")

        pages = connection.execute("SELECT ID, DATE, NUM, URL, CONTENT FROM PAGES where id > 0")

        for page in pages:
            soup = bs4.BeautifulSoup(page[4], "html.parser")
            elements = soup.select(self.item_link_selector)
            for element in elements:
                url = element.find("a")["href"]
                comments = element.select("li")[2]
                try:
                    dt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    cursor = connection.execute('''INSERT INTO ITEMS (DATE, PAGE_ID, URL, CONTENT) VALUES(?, ?, ?, ?)''', (dt, page[0], url, ''))
                    
                    connection.execute(f"UPDATE ITEMS SET COMMENTS = '{comments}' WHERE ID = {cursor.lastrowid}")
                except:
                    pass

                print(url)

            connection.commit()
        connection.close()
