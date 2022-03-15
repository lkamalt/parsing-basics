# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять
# только новые вакансии/продукты в вашу базу.
import pymongo

from config.mongo_conf import HOST, PORT
from tools.common import get_dict_hash
from tools.files import get_data_from_json
from tools.mongo import show_collection


def add_data_to_db(data):
    """
    Добавляет данные из списка data в базу данных MongoDB
    :param data: список словарей, каждый словарь соответствует одному объекту (вакансии) и содержит данные об объекте
    :type data: List[Dict]
    """
    if data is None:
        return

    with pymongo.MongoClient(HOST, port=PORT) as client:
        # База данных
        db_jobs = client.db_jobs
        # Коллекция
        jobs = db_jobs.jobs

        for item_dict in data:
            # Вычисляем хэш словаря объекта
            item_hash = get_dict_hash(item_dict)
            # Создаем новый словарь с дополнительным полем _id, значение которого будет равно хэшу объекта
            item_dict_and_id = {'_id': item_hash, **item_dict}
            # Пытаемся добавить объект в базу, в случае ошибки объект не добавляется, в консоль выводится текст,
            # почему объект не добавился
            try:
                jobs.insert_one(item_dict_and_id)
            except Exception as e:
                print(f'Ошибка при добавлении объекта в БД: {e}.\nОбъект {item_hash} не будет добавлен в базу.')

        # Отобразим всю коллекцию
        show_collection(jobs)


def main():
    """
    Основная функция
    Считывает данные из json-файла в виде списка словарей, каждый словарь содержит информацию об объекте, в данном
    случае вакансии из hh.ru
    Записывает считанные данные в базу данных MongoDB
    """
    # Считываем данные из файла
    data = get_data_from_json('../lesson2/result.json')
    # Записываем считанные данные в БД
    add_data_to_db(data)


# Вызов основной функции
main()
