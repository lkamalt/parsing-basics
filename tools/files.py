import json
import pandas as pd

# Кодировка по умолчанию для файлов
FILE_ENCODING = 'utf8'


def save_data_to_json(file_name, data):
    """
    Записывает данные data в файл по заданному пути file_name
    :param file_name: путь, по которому будет сохранен файл с данными data
    :type file_name: str
    :param data: сохраняемые данные
    :type data: typing.Any
    """
    with open(file_name, 'w', encoding=FILE_ENCODING) as f:
        json.dump(data, f)


def get_data_from_json(file_name):
    """
    Считывает данные из json-файла
    :param file_name: название файла, который необходимо считать
    :type file_name: str
    :rtype: typing.Any
    """
    with open(file_name, 'r', encoding=FILE_ENCODING) as f:
        return json.load(f)


def save_dicts_list_as_csv(file_name, dicts_list):
    """
    Сохраняет список словарей в виде таблицы, csv-файла
    :param file_name: название файла, куда будут сохранены данные dicts_list
    :type file_name: str
    :param dicts_list: список словарей
    :type dicts_list: List[Dict]
    """
    df = pd.json_normalize(dicts_list)
    df.to_csv(file_name, sep=';', encoding=FILE_ENCODING, index=False)
