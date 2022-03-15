import json
import hashlib

from tools.strs import remove_nbsp


def has_any_none(lst):
    """
    Возвращает флаг о наличии None в списке
    :param lst: анализируемый список
    :type lst: List
    :rtype: bool
    """
    return lst.count(None) != 0


def clear_dict_from_nbsp(item_dict):
    """
    Заменяет символы неразрывного пробела в строковых значениях словаря item_dict
    :param item_dict: словарь объекта
    :type item_dict: Dict
    """
    for key, value in item_dict.items():
        if isinstance(value, str):
            item_dict[key] = remove_nbsp(value)


def get_dict_hash(item_dict):
    """
    Генерирует MD5 хэш для словаря
    :param item_dict: словарь объекта
    :type item_dict: Dict
    :rtype: str
    """
    dict_hash = hashlib.md5()
    # Сортируем словарь по ключу, сериализуем словарь в json-строку, преобразуем эту строку в строку байт
    # Сортируем для случая, если ключи будут расположены в разном порядке
    dict_json_encoded = json.dumps(item_dict, sort_keys=True).encode()
    dict_hash.update(dict_json_encoded)
    return dict_hash.hexdigest()
