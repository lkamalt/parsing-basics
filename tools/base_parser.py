from pprint import pprint
import pymongo

from config.mongo_conf import HOST, PORT
from tools.files import save_data_to_json
from tools.mongo import add_item_to_collection, show_collection


class BaseParser:
    """ Базовый класс парсера """

    def __init__(self):
        # Список собранных на сайте данных - список словарей, каждый из которых содержит параметры одного объекта
        self._result = []

    @property
    def main_url(self):
        """
        Возвращает адрес сайта, который будет парситься
        :rtype: str
        """
        raise NotImplementedError('Не реализовано обязательное свойство')

    @property
    def db_name(self):
        """
        Возвращает название базы данных, куда будут сохранены собранные на сайта данные
        :rtype: str
        """
        return NotImplementedError('Не реализовано обязательное свойство')

    @property
    def collection_name(self):
        """
        Возвращает название коллекции базы данных, куда будут сохранены собранные на сайта данные
        :rtype: str
        """
        return NotImplementedError('Не реализовано обязательное свойство')

    def parse(self):
        """ Основная функция, производит парсинг сайта """
        raise NotImplementedError('Не реализован обязательный метод')

    def get_result(self):
        """
        Возвращает результат парсинга - список словарей, каждый словарь соответствует одной новости и содержит
        информацию о ней
        :rtype: List[Dict]
        """
        return self._result

    def print_result(self):
        """ Выводит результат парсинга в консоль - отображает список словарей """
        for news in self._result:
            pprint(news)

    def save_result_to_db(self):
        """ Добавляет собранные данные в базу данных MongoDB """
        if not self._result:
            return

        with pymongo.MongoClient(HOST, port=PORT) as client:
            # База данных
            db = client[self.db_name]
            # Коллекция
            collection = db[self.collection_name]

            # Добавляем объекты в коллекцию
            add_item_to_collection(self._result, collection)
            # Выводим коллекцию в консоль
            show_collection(collection)

    def save_result_to_json(self, file_name):
        """
        Сохраняет результат в json-файле
        :param file_name: название файла
        :type file_name: str
        """
        if self._result:
            save_data_to_json(file_name, self._result, ensure_ascii=False)
