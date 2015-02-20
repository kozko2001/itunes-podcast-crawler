# -*- coding: utf-8 -*-
from scrapy import Spider, Selector, Request
from itunes.items import ItunesItem
import re


def get_id_from_url(url):
    """
    extract the itunes id from an url
    """
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
        sel = Selector(response)
        selector = "div#genre-nav div ul li a.top-level-genre::attr(href)"
        urls = sel.css(selector).extract()

        for url in urls:
            yield Request(url, callback=self.parse_alpha)

    def parse_alpha(self, response):
        """ extract the alpha letters links"""
        sel = Selector(response)
        urls = sel.css("ul.alpha li a::attr(href)").extract()

        for url in urls:
            yield Request(url, callback=self.parse_page)

    def parse_page(self, response):
        """ Extract the paginate numbers links """
        sel = Selector(response)
        selector = ("ul.paginate li a:not(a.paginate-more)"
                    ":not(a.paginate-previous)"
                    "::attr(href)")
        urls = sel.css(selector).extract()
        self.parse_podcastlist(response)

        for url in urls:
            yield Request(url, callback=self.parse_podcastlist)

    def parse_podcastlist(self, response):
        """Extract podcast name and url from the list of podcasts"""
        sel = Selector(response)
        urls = sel.css("div#selectedcontent div ul li a::attr(href)").extract()
        names = sel.css("div#selectedcontent div ul li a::text").extract()

        for url, name in zip(urls, names):
            _id = get_id_from_url(url)
            item = ItunesItem(name=name, url=url, itunesId=_id)
            yield item
