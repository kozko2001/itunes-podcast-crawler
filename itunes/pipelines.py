# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ItunesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['itunesId'] in self.ids_seen:
            raise DropItem("Duplicated id... %s", item)
        else:
            self.ids_seen.add(item['itunesId'])
            return item
