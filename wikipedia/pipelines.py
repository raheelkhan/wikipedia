# -*- coding: utf-8 -*-

from scrapy.utils.markup import remove_tags
import re


class WikipediaPipeline(object):
    def process_item(self, item, spider):
        # cleanup introduction
        item['introduction'] = ''.join(
            re.sub(r'\[\d+\]', '', remove_tags(x)) for x in item['introduction'])

        # clean up techniques
        for heading, text in item['content']['Techniques'].iteritems():
            item['content']['Techniques'][heading] = re.sub(
                r'\[\d+\]', '', remove_tags(text))

        # cleanup legal issues
        for heading, text in item['content']['Legal issues'].iteritems():
            item['content']['Legal issues'][heading] = re.sub(
                r'\[\d+\]', '', remove_tags(text))

        # clen up methods to prevent scraping
        item['content']['Methods to prevent web scraping'] = [
            remove_tags(x) for x in item['content']['Methods to prevent web scraping']]

        # cleanup references
        item['content']['References'] = [
            re.sub('"', '', remove_tags(x)) for x in item['content']['References']]
        return item
