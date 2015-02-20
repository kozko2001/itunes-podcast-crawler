# -*- coding: utf-8 -*-

# Scrapy settings for itunes project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'itunes'

SPIDER_MODULES = ['itunes.spiders']
NEWSPIDER_MODULE = 'itunes.spiders'
ITEM_PIPELINES = {
    'itunes.pipelines.ItunesPipeline': 100
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'itunes (+http://www.yourdomain.com)'
