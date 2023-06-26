# Используем selenium, потому что нужно отрендерить страницу и выполнить AJAX.
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
import sqlite3


class Record:
    def __init__(self, year: str, title: str, annotation: str, authors: str, text: str, url: str, theme: str):
        self.year = year
        self.title = title
        self.annotation = annotation
        self.authors = authors
        self.text = text
        self.url = url
        self.theme = theme


def get_data(driver: WebDriver, page: int, index: int, records: list):
    # Устанавливаем таймер максимального ожидания ajax на 7 секунд
    driver.implicitly_wait(7)
    # driver.get(url)
    # driver.find_elements_by_css_selector('li>button')[0].click()

    # Извлекаем нужные нам блоки
    ul = driver.find_element(By.ID, 'search-results')
    li = ul.find_elements(By.TAG_NAME, "li")

    element = li[index].find_element(By.CLASS_NAME, 'title')
    title = element.find_element(By.TAG_NAME, "a").text
    url = element.find_element(By.TAG_NAME, "a").get_attribute('href')
    print("title - ", title)
    print("link - ", url)
    driver.get(url)

    try:
        author = driver.find_element(By.XPATH,
                                     '//*[@id="body"]/div[3]/div/span/div[2]/div[1]/div[1]/ul/li/span').text
    except NoSuchElementException:
        author = driver.find_element(By.XPATH,
                                     '//*[@id="body"]/div[3]/div/span/div[2]/div[1]/div[1]/ul/li/a').text
    print("autor - ", author)

    theme = driver.find_element(By.XPATH,
                                '//*[@id="body"]/div[3]/div/span/div[2]/div[5]/div[2]/ul/li/a').text
    print("theme - ", theme)

    year = driver.find_element(By.XPATH,
                               '//*[@id="body"]/div[3]/div/span/div[2]/div[5]/div[1]/div[2]/div[1]/time').text
    print("year - ", year)
    try:
        annotation = driver.find_element(By.XPATH,
                                         '//*[@id="body"]/div[3]/div/span/div[2]/div[7]/div/p').text
    except NoSuchElementException:
        annotation = "None"

    print("annotation - ", annotation)

    ocr = driver.find_element(By.CLASS_NAME, 'ocr')
    pis = ocr.find_elements(By.TAG_NAME, 'p')

    text = "\n".join([i.text for i in pis])

    records.append(Record(title=title,
                          annotation=annotation,
                          authors=author,
                          year=year,
                          text=text,
                          url=url,
                          theme=theme))
    driver.back()


def insert_data(path: str, data: list[Record]):
    with sqlite3.connect(path) as connection:
        cursor = connection.cursor()
        insert_query = 'INSERT INTO topics (author, title, annotation, content, url, year,theme) VALUES (?, ?, ?, ?, ?,?,?)'
        for item in data:
            cursor.execute(
                insert_query,
                (item.authors,
                 item.title,
                 item.annotation,
                 item.text,
                 item.url,
                 item.year,
                 item.theme)
            )
        connection.commit()


def get_data_from_db(path, keyword='семантический анализ текста'):
    # Достаем значения из БД
    with sqlite3.connect(path) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM main.topics')

        # Выводим значения в консоль
        rows = cursor.fetchall()
    return rows


def get_url(keyword, page):
    return 'https://cyberleninka.ru/search?q=' + keyword + '&page=' + str(page)


def parse(keyword="семантический анализ текста", page_count=10):
    records = []
    service = Service(executable_path=".chromedriver.exe")
    with webdriver.Chrome(service=service) as driver:
        for page in range(1, page_count + 1):
            driver.get(get_url(keyword, page))
            ul = driver.find_element(By.ID, 'search-results')
            max_count = len(ul.find_elements(By.TAG_NAME, "li"))
            if page != 0:
                print("Page - ", page)
                for index in range(max_count):
                    get_data(driver=driver,
                             page=get_url(keyword, page),
                             index=index,
                             records=records)
    return records


if __name__ == '__main__':
    records = parse(keyword='семантический анализ подобия текста',
                    page_count=10)
    insert_data("../topics.sqlite", records)
    print(get_data_from_db("../topics.sqlite"))

    # create table topics
    # (
    #     id         integer not null
    #         constraint topics_pk
    #             primary key autoincrement,
    #     author     TEXT    not null,
    #     title      TEXT    not null,
    #     annotation TEXT    null on conflict ignore,
    #     content    TEXT,
    #     url        TEXT,
    #     year       VARCHAR,
    #     theme      TEXT,
    #     unique (author, title) on conflict ignore
    # );
