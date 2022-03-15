from pprint import pprint

from tools.common import get_dict_hash


def delete_all_in_collection(collection):
    """
    Удаляет все документы из заданной коллекции collection
    :param collection: коллекция в БД
    :type collection: Collection
    """
    collection.delete_many({})


def show_collection(collection):
    """
    Отображает все документы, хранимые в заданной коллекции collection в БД
    :param collection: коллекция в БД
    :type collection: Collection
    """
    for doc in collection.find({}):
        pprint(doc)


def add_item_to_collection(item_dicts_list, collection):
    """
    Добавляет объекты из списка item_dicts_list в коллекцию collection базы данных MongoDB
    :param item_dicts_list: список объектов - словарей
    :type item_dicts_list: List[Dict]
    :param collection: коллекция в базе данных
    :type collection: Collection
    """
    for item_dict in item_dicts_list:
        # Вычисляем хэш словаря объекта
        item_hash = get_dict_hash(item_dict)
        # Создаем новый словарь с дополнительным полем _id, значение которого будет равно хэшу объекта
        item_dict_and_id = {'_id': item_hash, **item_dict}
        # Пытаемся добавить объект в базу, в случае ошибки объект не добавляется, в консоль выводится текст,
        # почему объект не добавился
        try:
            collection.insert_one(item_dict_and_id)
        except Exception as e:
            print(f'Ошибка при добавлении объекта в БД: {e}.\nОбъект {item_hash} не будет добавлен в базу.')
