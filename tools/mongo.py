from pprint import pprint


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
