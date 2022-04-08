# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import json

from tools.config import HOST, PORT
from tools.str_processing import get_number, get_letters


class JobParserPipeline:
    def __init__(self):
        self.db_client = MongoClient(HOST, PORT)
        self.db_mongo = self.db_client.vacancies
        # Список собранных вакансий
        self._vacancies = []

    def close_spider(self, spider):
        # Закрываем соединение с базой
        self.db_client.close()
        # Записываем результат в файл
        with open(f'{spider.name}_vacancies.json', 'w', encoding='utf-8') as f:
            json.dump(self._vacancies, f, ensure_ascii=False)

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['salary_curr'] = self.process_salary(item['salary'])
            del item['salary']

        # Сохраняем вакансию в словаре для записи в файл
        self._vacancies.append(ItemAdapter(item).asdict())

        # Записываем вакансию в базу данных
        collection = self.db_mongo[spider.name]
        try:
            collection.insert_one(item)
        except Exception as e:
            print(f'Не удалось добавить объект в базу данных: {str(e)}')

        return item

    def process_salary(self, salary):
        if not salary:
            return [None] * 3

        salary_clean = [s.lower().strip() for s in salary if s.split()]

        salary_numbers = []
        max_number_idx = 0
        for idx, s in enumerate(salary_clean):
            number = get_number(s)
            if number is not None:
                max_number_idx = idx
                salary_numbers.append(number)

        if not salary_numbers:
            return [None] * 3

        if len(salary_numbers) == 1:
            # Если есть 'от', то задано только минимальное значение зарплаты [value, None]
            if 'от' in salary_clean:
                salary_numbers.append(None)
            # Если есть 'до', то задано только максимальное значение зарплаты [None, value]
            elif 'до' in salary_clean:
                salary_numbers.insert(0, None)

        salary_curr = get_letters(salary_clean[max_number_idx + 1]).upper()

        return *salary_numbers, salary_curr
