# -*- coding: utf-8 -*-
from scrapy import Spider, Selector, Request
from itunes.items import ItunesItem
import re
import datetime
import json
import time


def test(l):
    return l
    print l
    x = [l[0]] if l else l
    print x
    return x
    #return l


def get_id_from_url(url):
    g = re.search("id(\\d+)", url)
    return g.group(1)


class ItunesspiderSpider(Spider):
    name = "itunesSpider"
    allowed_domains = ["itunes.apple.com"]
    start_urls = (
        "https://itunes.apple.com/us/genre/podcasts/id26?mt=2",
    )

    def parse(self, response):
        """ Extract the main genres"""
        self.popular = {}
        sel = Selector(response)

        names = sel.css("div#genre-nav div ul li a.top-level-genre::text").extract()
        urls  = sel.css("div#genre-nav div ul li a.top-level-genre::attr(href)").extract()
        urls_subgenres  = sel.css("div#genre-nav div ul.top-level-subgenres li a::attr(href)").extract()

        for url in urls_subgenres:
            yield Request(url, callback=self.parse_popularity)

        for url in test(urls):
            yield Request(url, callback=self.parse_alpha)

    def parse_popularity(self, response):
        sel = Selector(response)
        urls = sel.css("div#selectedcontent div ul li a::attr(href)").extract()
        ids = [get_id_from_url(url) for url in urls]

        for _id in ids:
            if _id in self.popular:
                self.popular[_id] += 1
            else:
                self.popular[_id] = 1

    def parse_alpha(self, response):
        """ extract the alpha letters links"""
        sel = Selector(response)
        urls = sel.css("ul.alpha li a::attr(href)").extract()

        self.parse_popularity(response)

        for url in test(urls):
            yield Request(url, callback=self.parse_page)

    def parse_page(self, response):
        """ Extract the paginate numbers links """
        sel = Selector(response)
        urls = sel.css("ul.paginate li a:not(a.paginate-more):not(a.paginate-previous)::attr(href)").extract()
        self.parse_podcastlist(response)

        for url in test(urls):
            yield Request(url, callback=self.parse_podcastlist)

    def parse_podcastlist(self, response):
        """ TODO COMMENT """
        sel = Selector(response)
        urls = sel.css("div#selectedcontent div ul li a::attr(href)").extract()
        names = sel.css("div#selectedcontent div ul li a::text").extract()

        for url, name in zip(urls, names):
            item = ItunesItem(name=name, url=url)

            _id = get_id_from_url(url)
            item["itunesId"] = _id
            url = "https://itunes.apple.com/lookup?id=%s" % _id
            popular = self.popular[_id] if _id in self.popular else 0
            item["popular"] = popular

            yield item
            #yield Request(url,
            #              callback=self.parse_podcast,
            #              meta={"item": item})

    def parse_podcast(self, response):
        """ TODO COMMENT """
        item = response.request.meta["item"]
        jsonresponse = json.loads(response.body_as_unicode())
        date = jsonresponse["results"][0]["releaseDate"]
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        if date > datetime.datetime.now() - datetime.timedelta(days=366):
            item["feedUrl"] = jsonresponse["results"][0]["feedUrl"]
            item["date"] = jsonresponse["results"][0]["releaseDate"]
            item["imageUrl"] = jsonresponse["results"][0]["artworkUrl600"]

            yield item
