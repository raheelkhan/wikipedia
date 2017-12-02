# -*- coding: utf-8 -*-
import scrapy
from wikipedia.items import WikipediaItem
from urlparse import urljoin, urlparse
import re


class WebscrapingSpider(scrapy.Spider):
    """
    Spider for Webscraping page in Wikipedia
        :param scrapy.Spider: 
    """
    name = 'webscraping'
    allowed_domains = ['https://en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Web_scraping']

    def parse(self, response):
        item = WikipediaItem()

        item['title'] = response.xpath(
            '//*[@id="firstHeading"]/text()').extract_first()

        item['parent'] = dict()
        item['parent']['link'] = self.__join_url(response.xpath(
            '//*[@id="mw-content-text"]/div/div[1]/a/@href').extract_first())
        item['parent']['title'] = response.xpath(
            '//*[@id="mw-content-text"]/div/div[1]/a/@title').extract_first()

        item['introduction'] = response.xpath(
            '//div[@class="mw-parser-output"]/div[@id="toc"]/preceding-sibling::p').extract()

        item['categories'] = list()
        categories = response.xpath(
            '//div[@class="mw-normal-catlinks"]/ul/li/a')
        for category in categories:
            link = dict()
            link['name'] = category.xpath('./text()').extract_first()
            link['link'] = self.__join_url(category.xpath('./@href').extract_first())
            item['categories'].append(link)

        item['languages'] = list()
        languages = response.xpath(
            '//li[contains(@class,"interlanguage-link")]/a')
        for language in languages:
            link = dict()
            link['name'] = language.xpath('./text()').extract_first()
            link['link'] = self.__join_url(
                language.xpath('./@href').extract_first())
            item['languages'].append(link)

        """
        Parse Content Area
        """
        item['content'] = content = dict()
        # parse techniques
        self.__parse_techniques(content, response)
        # parse software
        self.__parse_software(content, response)
        # parse legal issues
        self.__parse_legal_issues(content, response)
        # parse prevent scraping
        self.__parse_prevent(content, response)
        # parse see also
        self.__parse_see_also(content, response)
        # parse references
        self.__parse_referenes(content, response)
        """
        End Content Area
        """

        yield item

    def __parse_referenes(self, content, response):
        reference_sel = response.xpath('//*[@id="References"]')
        heading = reference_sel.xpath('./text()').extract_first()
        content[heading] = list()
        references = response.xpath(
            '//*[@class="reference-text"]/descendant::*[1]').extract()
        content[heading].extend(references)

    def __parse_see_also(self, content, response):
        see_also_sel = response.xpath('//*[@id="See_also"]')
        heading = see_also_sel.xpath('./text()').extract_first()
        content[heading] = list()
        see_also_list_sel = see_also_sel.xpath(
            './ancestor::h2/following-sibling::div/ul/li')
        for link in see_also_list_sel:
            content[heading].append(
                dict(name=link.xpath('./a/text()').extract_first(), link=self.__join_url(
                    link.xpath('./a/@href').extract_first())))

    def __parse_prevent(self, content, response):
        prevent_sel = response.xpath(
            '//*[@id="Methods_to_prevent_web_scraping"]')
        heading = prevent_sel.xpath('./text()').extract_first()
        content[heading] = list()
        prevent_sel_list = prevent_sel.xpath(
            './ancestor::h2/following-sibling::ul/li')
        for prevention in prevent_sel_list:
            content[heading].append(prevention.xpath('.').extract_first())

    def __parse_legal_issues(self, content, response):
        legal_issues = response.xpath('// *[@id="Legal_issues"]')
        heading = legal_issues.xpath('./text()').extract_first()
        content[heading] = dict()
        usa_heading = legal_issues.xpath(
            './ancestor::h2/following-sibling::h3/span[1]/text()').extract_first()
        content[heading][usa_heading] = ' '.join(legal_issues.xpath(
            './ancestor::h2/following-sibling::h3/following-sibling::p[following-sibling::h3]').extract())
        outside_usa_heading = legal_issues.xpath(
            './ancestor::h2/following-sibling::h3[2]/span[1]/text()').extract_first()
        content[heading][outside_usa_heading] = ' '.join(legal_issues.xpath(
            './ancestor::h2/following-sibling::h3[2]/following-sibling::p[position() < 4]').extract())

    def __parse_software(self, content, response):
        software_sel = response.xpath('//*[@id="toc"]/ul/li[2]')
        heading = software_sel.xpath('.//a/span[2]/text()').extract_first()
        content[heading] = dict()
        example_tools_sel = software_sel.xpath('.//ul/li[1]')
        example_tools_name = example_tools_sel.xpath(
            './/a/span[2]/text()').extract_first()
        example_tools_link = example_tools_sel.xpath(
            './/a/@href').extract_first().replace('#', '')
        example_tools = []
        example_tools_list_sel = response.xpath(
            '//*[@id="{id}"]/ancestor::h3/following-sibling::ul[1]/li'.format(
                id=example_tools_link))
        for tool_list in example_tools_list_sel:
            tool = dict()
            tool['name'] = tool_list.xpath('.//a/@title').extract_first()
            tool['link'] = self.__join_url(tool_list.xpath('.//a/@href').extract_first())
            tool['description'] = tool_list.xpath('.//text()').extract()[-1]
            example_tools.append(tool)

        content[heading][example_tools_name] = example_tools

        example_tools_types = example_tools_sel.xpath('.//ul/li/a')
        for tool_type in example_tools_types:
            type_name = tool_type.xpath('.//span[2]/text()').extract_first()
            type_link = tool_type.xpath(
                './/@href').extract_first().replace('#', '')
            content[heading][type_name] = list()
            tools_list_sel = response.xpath(
                '//*[@id="{id}"]/ancestor::h4/following-sibling::ul[1]/li/a'.format(id=type_link))
            for tool_sel in tools_list_sel:
                tool = dict()
                tool['name'] = tool_sel.xpath('.//text()').extract_first()
                tool['link'] = self.__join_url(tool_sel.xpath('.//@href').extract_first())

                content[heading][type_name].append(tool)

    def __parse_techniques(self, content, response):
        techniques_sel = response.xpath('//*[@id="toc"]/ul/li[1]')
        heading = techniques_sel.xpath('.//a/span[2]/text()').extract_first()
        techniques_list = [x.replace('#', '') for x in techniques_sel.xpath(
            './/ul/li/a/@href').extract()]
        content[heading] = dict()
        for technique in techniques_list:
            text = response.xpath(
                '//*[@id="{id}"]/ancestor::h3/following-sibling::p[1]'.format(
                    id=technique)
            ).extract_first()
            content[heading][technique] = text

    def __join_url(self, url):

        if url is not None and urlparse(url).netloc == '':
            url = urljoin(WebscrapingSpider.allowed_domains[0], url)

        return url
