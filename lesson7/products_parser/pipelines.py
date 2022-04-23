# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from os.path import join
import scrapy
import json
import hashlib

from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from tools.config import HOST, PORT


class ProductsParserPipeline:
    def __init__(self):
        self.db_client = MongoClient(HOST, PORT)
        self.db_mongo = self.db_client.products
        self._products = []

    def close_spider(self, spider):
        # Закрываем соединение с базой
        self.db_client.close()
        # Записываем результат в файл
        with open(f'{spider.name}_products.json', 'w', encoding='utf-8') as f:
            json.dump(self._products, f, ensure_ascii=False, indent=4)

    def process_item(self, item, spider):
        # Сохраняем продукт в словаре для записи в файл
        self._products.append(ItemAdapter(item).asdict())

        # Добавляем продукт в базу данных
        collection = self.db_mongo[spider.name]
        try:
            collection.insert_one(item)
        except Exception as e:
            print(f'Не удалось добавить объект в базу данных: {e}')

        return item


class CastoramaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [el[1] for el in results if el[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_url_hash = hashlib.shake_256(request.url.encode()).hexdigest(5)
        item_url_hash = hashlib.shake_256(item['link'].encode()).hexdigest(5)
        return join(item_url_hash, f'{image_url_hash}.jpg')
