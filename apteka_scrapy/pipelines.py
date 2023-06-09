# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
from scrapy.exceptions import DropItem
from apteka_scrapy import settings
from apteka_scrapy.items import AptekaItem
import json
from scrapy.exporters import JsonLinesItemExporter


class AptekaScrapyPipeline:
    def process_item(self, item, spider):
        return item


class JsonPipeline:
    def __init__(self):
        self.file = open('result.json', 'wb')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        data = {
            "timestamp": item['timestamp'],
            "RPC": item['RPC'],
            "url": item['url'],
            "title": item['title'],
            "marketing_tags": item['marketing_tags'],
            "brand": item['brand'],
            "section": item['section'],
            "price_data": {
                "current": item['price'],
            },
            "stock": {
                "in_stock": item['in_stock'],
                "count": 1
            },
            "assets": {
                "main_image": item['main_image'],
            },
            "metadata": {
                "__description": item['description'],
                "СТРАНА ПРОИЗВОДИТЕЛЬ": item['location']
            },
            "variants": item['variants']
        }
        self.exporter.export_item(data)
        return item



