# -*- coding: utf-8 -*-

import scrapy


class WikipediaItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    parent = scrapy.Field()
    introduction = scrapy.Field()
    categories = scrapy.Field()
    languages = scrapy.Field()
    content = scrapy.Field()
    pass
