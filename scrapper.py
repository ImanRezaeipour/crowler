import datetime
import sqlite3

import bs4
import lxml
import requests


class Scrapper():
    def __init__(self, domain_name, pagination_address, page_name, parent_link_selector, grab_tags):
        self.domain_name = domain_name
        self.pagination_address = pagination_address
        self.page_name = page_name
        self.parent_link_selector = parent_link_selector
        self.grab_tags = grab_tags

    def save_pages_to_sqlite(self, file_name):
        page_url = self.domain_name + self.pagination_address
        connection = sqlite3.Connection(file_name)
        connection.execute("CREATE TABLE IF NOT EXISTS PAGES (ID INTEGER PRIMARY KEY AUTOINCREMENT, DATE DATETIME, NUM INT, URL NVARCHAR, CONTENT XML)")

        page_index = 2900
        while True:
            url = page_url + self.page_name.format(page_index) if page_index > 0 else page_url
            page_response = requests.get(url)

            if (page_response.status_code == 404):
                break
            
            dt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            connection.execute('''INSERT INTO PAGES (DATE, NUM, URL, CONTENT) VALUES(?, ?, ?, ?)''', (dt, page_index, url, page_response.content))

            print(url)
            page_index += 1

            if page_index % 100 == 0:
                connection.commit()

        connection.commit()
        connection.close()

    def save_items_to_sqlite(self, file_name):
        connection = sqlite3.Connection(file_name)
        connection.execute("CREATE TABLE IF NOT EXISTS ITEMS (ID INTEGER PRIMARY KEY AUTOINCREMENT, DATE DATETIME, PAGE_ID INT, URL NVARCHAR, CONTENT XML)")

        pages_cusor = connection.execute("SELECT ID, DATE, NUM, URL, CONTENT FROM PAGES where id > 35")

        for page in pages_cusor:
            soup = bs4.BeautifulSoup(page[4], "html.parser")
            elem = soup.select(self.parent_link_selector)
            for e in set([e["href"] for e in elem[0].find_all("a") if '?' in e['href']]):
                url = self.domain_name + e
                try:
                    item_response = requests.get(url)
                    dt = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    connection.execute('''INSERT INTO ITEMS (DATE, PAGE_ID, URL, CONTENT) VALUES(?, ?, ?, ?)''', (dt, page[0], url, item_response.content))
                except:
                    pass

                print(url)

            connection.commit()
        connection.close()

    def save_details_to_sqlite(self, file_name):
        connection = sqlite3.Connection(file_name)
        connection.execute("CREATE TABLE IF NOT EXISTS DETAILS (ID INTEGER PRIMARY KEY AUTOINCREMENT, ITEM_ID INT)")

        for grab_tag_key, grab_tag_value in self.grab_tags.items():
            columns_cursor = connection.execute("PRAGMA TABLE_INFO(DETAILS)")
            for column in columns_cursor:
                if column[1].lower() == grab_tag_key.lower():
                    break
            else:
                connection.execute(f"ALTER TABLE DETAILS ADD COLUMN {grab_tag_key} NVARCHAR")

        items_cusor = connection.execute("SELECT ID, DATE, PAGE_ID, URL, CONTENT FROM ITEMS where id > 1510")

        for item in items_cusor:
            soup = bs4.BeautifulSoup(item[4], "html.parser")

            connection.execute('''INSERT INTO DETAILS (ITEM_ID) VALUES(?)''', (item[0],))

            for grab_tag_key, grab_tag_value in self.grab_tags.items():
                elem = soup.select(grab_tag_value)
                if elem != None and len(elem) > 0:

                    connection.execute(f"UPDATE DETAILS SET {grab_tag_key} = '{str(elem[0].text).strip()}' WHERE ITEM_ID = {item[0]}")

                    print(grab_tag_key, elem[0].text)

            connection.commit()
        connection.close()
