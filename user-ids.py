import scrapy

from urllib.parse import urljoin, urlparse
from scrapy.crawler import CrawlerProcess
from scrapy import signals

import io
import json

class UsersSpider(scrapy.Spider):
    name = "user-ids"
    urls = [
        "https://www.behance.net/search/users/?sort=appreciations&ordinal=200"
    ]

    ids = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(UsersSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        content = open('user_ids.json', 'r').read()

        if content == '':
            content = '[]'

        content = '[]'
        data = json.load(io.StringIO(content))

        data.extend(self.ids)

        open('user_ids.json', 'w').write(json.dumps(data, indent=4))

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for links in response.css('h3.ProfileRow-displayName-YQn'):
            link = links.css('a::attr(href)').get()

            self.ids.append(urljoin(link, urlparse(link).path) + "/projects")


process = CrawlerProcess()

process.crawl(UsersSpider)
process.start()