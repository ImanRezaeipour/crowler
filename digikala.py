import datetime
import sqlite3

import bs4
import lxml
import requests

def save_pages_to_sqlite():
        page_url = 'https://api.digikala.com/v1/product/{}/'
        connection = sqlite3.Connection('digikala.db')
        connection.execute(
            "CREATE TABLE IF NOT EXISTS ITEMS (ID INTEGER PRIMARY KEY AUTOINCREMENT, DATE DATETIME, NUM INT, URL NVARCHAR, CONTENT XML)")

        page_index = 1
        while True:
            url = page_url.format(page_index)
            page_response = requests.get(url)

            if (page_response.status_code == 404):
                break

            connection.execute('''INSERT INTO ITEMS (DATE, NUM, URL, CONTENT) VALUES(?, ?, ?, ?)''', (
                datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), page_index, url, page_response.content))

            print(url)
            page_index += 1

            if page_index % 100 == 0:
                connection.commit()

        connection.commit()
        connection.close()


save_pages_to_sqlite()
