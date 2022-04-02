# 1. Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
#   1) название источника;
#   2) наименование новости;
#   3) ссылку на новость;
#   4) дата публикации.
# 2. Сложить собранные новости в БД.
import requests
import time
from urllib.parse import urljoin
from lxml import html

from config.request_conf import USER_AGENT
from tools.base_parser import BaseParser


class LentaRuParser(BaseParser):
    """ Класс парсера новостного сайта lenta.ru """

    def __init__(self):
        super().__init__()
        # Преобразованный для парсинга ответ
        self._dom = None
        # Ответ сайта
        self._response = None

    @property
    def main_url(self):
        # Ссылка на новостной сайт, который будет парситься
        return 'https://lenta.ru/'

    @property
    def db_name(self):
        return 'db_news'

    @property
    def collection_name(self):
        return 'news'

    def _make_request(self, url):
        """
        Делает запрос по указанному адресу url
        :param url: адрес запроса
        :type url: str
        :rtype: requests.Response
        """
        # Заголовок запроса
        header = {'User-Agent': USER_AGENT}
        return requests.get(url, headers=header)

    def _get_publish_date(self, news_url):
        """
        Извлекает дату публикации новости из ответа на запрос по адресу news_url
        :param news_url: ссылка на новость
        :type news_url: str
        :rtype: str
        """
        # Делаем отдельный запрос на страницу самой новости
        response = self._make_request(news_url)
        dom = html.fromstring(response.text)
        # Извлекаем информацию о дате публикации
        text_elem = dom.xpath('//time[@class="topic-header__item topic-header__time"]/text()')
        return text_elem[0] if text_elem else ''

    def _parse_mini_cards(self):
        """ Парсинг карточек с новостями без заголовка """
        # Названия карточек новостей без заголовка
        mini_cards_names = [
            'card-mini _topnews',  # новости в начале
            'card-mini _compact',  # новости сбоку
            'card-mini _longgrid'  # новости маленькие карточки дальше
        ]

        print('Обработка карточек 1/3')
        self._parse_cards(mini_cards_names, body_class_name='card-mini__title')

    def _parse_big_cards(self):
        """ Парсинг маленьких карточек с новостями, у которых есть заголовок """
        # Название карточек новостей с заголовком
        big_cards_names = [
            'card-big _topnews _news',  # Самая первая новость
            'card-big _longgrid',  # Новости в середине страницы
            'card-big _slider _dark _popular _article'  # Популярные новости
        ]

        print('Обработка карточек 2/3')
        self._parse_cards(big_cards_names, 'card-big__title', 'card-big__rightcol')

    def _parse_photo_cards(self):
        """ Парсинг больших карточек, с новостью на фоне фото и у которых есть заголовок """
        # Названия карточек с новостями на фоне фотографии
        photo_cards_names = ['card-feature']

        print('Обработка карточек 3/3')
        self._parse_cards(photo_cards_names, 'card-feature__title', 'card-feature__description')

    def _parse_cards(self, cards_names, title_class_name=None, body_class_name=None):
        """
        Парсинг новостных карточек, соответствующих одному типу
        :param cards_names: названия карточек
        :type cards_names: List[str]
        :param title_class_name: название класса, где содержится заголовок новости
        :type title_class_name: str
        :param body_class_name: название класса, где содержится небольшое описание новости
        :type body_class_name: str
        """
        # Список элементов, соответствующим блокам с новостями
        cards = []
        for card_name in cards_names:
            cards.extend(self._dom.xpath(f'//a[@class="{card_name}"]'))

        print('0.00%', end='')
        for idx, card in enumerate(cards):
            # Парсим карточку
            news = self._parse_card(card, title_class_name, body_class_name)
            self._result.append(news)

            # Задержим на секунду
            time.sleep(1)

            # Отображаем процент выполнения
            progress = (idx + 1) / len(cards) * 100
            print(f'\r{progress:.2f}%', end='')
        print()

    def _parse_card(self, card, title_class_name, body_class_name):
        """
        Парсит одну карточку с новостью
        :param card: обрабатываемая карточка
        :type card: Element
        :param title_class_name: название класса, где содержится заголовок новости
        :type title_class_name: str
        :param body_class_name: название класса, где содержится небольшое описание новости
        :type body_class_name: str
        :return: словарь с информацией о новости
        :rtype: Dict
        """
        # Относительная ссылка на новость
        rel_news_url = card.xpath('.//@href')[0]
        # Собираем полную ссылку на новость
        news_url = urljoin(self.main_url, rel_news_url)
        # Пробуем извлечь дату публикации, делая запрос на адрес самой новости
        publish_date = self._get_publish_date(news_url)

        # Заголовок новости
        title = card.xpath(f'.//h3[@class="{title_class_name}"]/text()') if title_class_name else None
        # Описание новости
        body = card.xpath(f'.//span[@class="{body_class_name}"]/text()') if body_class_name else None

        # Словарь с параметрами новости
        news = {
            'source': self.main_url,
            'title': title[0] if title else '',
            'body': body[0] if body else '',
            'link': news_url,
            'publish_date': publish_date
        }
        return news

    def parse(self):
        """
        Основная функция
        Запускает процесс парсинга сайта lenta.ru
        """
        # Ответ на запрос
        response = self._make_request(self.main_url)
        # Объект для парсинга
        self._dom = html.fromstring(response.text)

        # Парсим группы карточек
        self._parse_mini_cards()
        self._parse_big_cards()
        self._parse_photo_cards()


if __name__ == '__main__':
    # Парсер
    parser = LentaRuParser()
    # Запускаем парсинг сайта
    parser.parse()

    # Добавляем полученный список новостей в базу данных
    parser.save_result_to_db()
    # Сохраняем результат парсинга (список словарей) в файл
    parser.save_result_to_json('result.json')
