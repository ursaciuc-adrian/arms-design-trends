import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals

import io
import json

class UsersSpider(scrapy.Spider):
    name = "users"
    urls = []

    users = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(UsersSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        content = open('users.json', 'r').read()

        if content == '':
            content = '[]'

        content = '[]'
        data = json.load(io.StringIO(content))

        data.extend(self.users)

        open('users.json', 'w').write(json.dumps(data, indent=4))

    def start_requests(self):
        self.urls = json.load(open('user_ids.json', 'r'))

        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        user = {
            "link": response.url
        }

        user["username"] = user["link"].split('/')[3].lower()
        user["avatar"] = response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/main/div[2]/div[1]/div[1]/div[1]/div/span/div/div/div/img/@src').get() 
        user["name"] = response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/main/div[2]/div[1]/div[1]/h1/text()').get() 
        user["position"] = response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/main/div[2]/div[1]/div[1]/div[2]/p[1]/text()').get() 

        stats = {}
        stats["project_views"] = int(response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/main/div[2]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[1]/td[2]/a/text()').get().replace(',', ''))
        stats["appreciations"] = int(response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/main/div[2]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[2]/td[2]/a/text()').get().replace(',', ''))
        stats["followers"] = int(response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/main/div[2]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[3]/td[2]/a/text()').get().replace(',', ''))
        stats["following"] = int(response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/main/div[2]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[4]/td[2]/a/text()').get().replace(',', ''))
        
        user["stats"] = stats

        projects = []
        for s_project in response.css('a.ProjectCoverNeue-coverLink-102'):
            link = s_project.css('a::attr(href)').get()
            project = {
                "id": link.split('/')[4],
                "link": link
            }
            projects.append(project)

        user["projects"] = projects

        self.users.append(user)

process = CrawlerProcess()

process.crawl(UsersSpider)
process.start()