# 1. Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
#   1) название источника;
#   2) наименование новости;
#   3) ссылку на новость;
#   4) дата публикации.
# 2. Сложить собранные новости в БД.
import requests
from urllib.parse import urljoin
from lxml import html
import pymongo
import time

from config.request_conf import USER_AGENT
from config.mongo_conf import HOST, PORT
from tools.mongo import add_item_to_collection, show_collection
from tools.files import save_data_to_json

# Ссылка на новостной сайт, который будет парситься
MAIN_URL = 'https://lenta.ru/'


def make_request(url):
    """
    Делает запрос по указанному адресу url
    :param url: адрес запроса
    :type url: str
    :rtype: requests.Response
    """
    # Заголовок запроса
    header = {'User-Agent': USER_AGENT}
    return requests.get(url, headers=header)


def get_publish_date(news_url):
    """
    Извлекает дату публикации новости из ответа на запрос по адресу news_url
    :param news_url: ссылка на новость
    :type news_url: str
    :rtype: str
    """
    # Делаем отдельный запрос на страницу самой новости
    response = make_request(news_url)
    dom = html.fromstring(response.text)
    # Извлекаем информацию о дате публикации
    text_elem = dom.xpath('//time[@class="topic-header__item topic-header__time"]/text()')
    return text_elem[0] if text_elem else ''


def parse_main_url_response(response):
    """
    Парсит ответ, полученный при запросе на новостной сайт lenta.ru
    :param response: ответ на запрос
    :type response: requests.Response
    :return: список новостей - список словарей, каждый словарь соответствует одной новости и содержит информацию о ней
    :rtype: List[Dict]
    """
    dom = html.fromstring(response.text)

    # Список элементов, соответствующим блокам с новостями
    cards = dom.xpath('//a[@class="card-mini _topnews"]')
    # Список словарей для каждой новости с распарсенными данными
    news_list = []

    print('Обработка данных:\n0.00%', end='')
    for idx, card in enumerate(cards):
        # Относительная ссылка на новость
        rel_news_url = card.xpath('.//@href')[0]
        # Собираем полную ссылку на новость
        news_url = urljoin(MAIN_URL, rel_news_url)
        # Пробуем извлечь дату публикации, делая запрос на адрес самой новости
        publish_date = get_publish_date(news_url)

        # Словарь с параметрами новости
        news = {
            'source': MAIN_URL,
            'title': card.xpath('.//span[@class="card-mini__title"]/text()')[0],
            'link': news_url,
            'publish_date': publish_date
        }
        news_list.append(news)

        # Задержим на секунду
        time.sleep(1)

        # Отображаем процент выполнения
        progress = (idx + 1) / len(cards) * 100
        print(f'\r{progress:.2f}%', end='')

    return news_list


def add_news_to_db(news_list):
    """
    Добавляет собранные новости в базу данных MongoDB
    :param news_list: список новостей - список словарей, каждый словарь соответствует одной новости и содержит
                        информацию о ней
    :type news_list: List[Dict]
    """
    with pymongo.MongoClient(HOST, port=PORT) as client:
        # База данных для новостей
        db_news = client.db_news
        # Коллекция для новостей
        news = db_news.news

        # Добавляем новости в коллекцию
        add_item_to_collection(news_list, news)
        # Выводим коллекцию в консоль
        show_collection(news)


def main():
    """
    Основная функция
    Запрашивает информацию с новостного сайта lenta.ru
    Парсит ответ, результатом является список новостей - список словарей, каждый словарь соответствует одной новости
    и содержит основную информацию о ней
    Полученный список новостей (словарей) сохраняет в базу данных MongoDB
    """
    # Ответ на запрос
    response = make_request(MAIN_URL)
    # Распарсенный ответ = список новостей в виде словарей
    news_list = parse_main_url_response(response)
    # Добавляем полученный список новостей в базу данных
    add_news_to_db(news_list)
    # Сохраним результат в json
    save_data_to_json('result.json', news_list, ensure_ascii=False)


# Вызов основной функции
main()
