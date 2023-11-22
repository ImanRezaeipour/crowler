from scrapper import Scrapper


scrapper = Scrapper(
    "https://songsara.net/",
    "tag/%D8%A2%D9%84%D8%A8%D9%88%D9%85-%D8%A8%DB%8C-%DA%A9%D9%84%D8%A7%D9%85-%D8%A8%D8%A7-%DA%A9%DB%8C%D9%81%DB%8C%D8%AA-flac/",
    "page/",
    "body > div.wrapper > div.container-fluid.container-headerfix > div > div > div.box-i",
    {"favorites": "body > div.wrapper > div.container-fluid.clear > div.row.flex-row-reverse > div > article > div:nth-child(3) > div > span > button > span",
     "comments": "body > div.wrapper > div.container-fluid.clear > div.row.flex-row-reverse > div > section.commentarea > div.commenttitle > span > span > a"})

scrapper.save_details_to_sqlite("songsara.db")
