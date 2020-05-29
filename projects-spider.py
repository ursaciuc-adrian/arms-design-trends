import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals

import io
import json

class ProjectsSpider(scrapy.Spider):
    name = "projects"
    urls = [
    ]

    projects = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ProjectsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        content = open('projects.json', 'r').read()

        if content == '':
            content = '[]'

        content = '[]'
        data = json.load(io.StringIO(content))

        data.extend(self.projects)

        open('projects.json', 'w').write(json.dumps(data, indent=4))

    def start_requests(self):
        users = json.load(open('users.json', 'r'))
        projects = [u["projects"] for u in users]
        project_links = []

        for p in projects:
            for p2 in p:
                project_links.append(p2["link"])

        self.urls = project_links

        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        project = {
            "id": 0,
            "link": response.url
        }

        project["id"] = response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/@data-id').get()
        project["user_id"] = response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div[1]/a/img/@data-id').get()
        project["title"] = response.xpath('/html/body/div[2]/div[1]/div/div/div/div[1]/div[1]/div/div[2]/div[1]/figcaption/span/text()').get()

        creative_fields = []
        for s_creative_field in response.css('li.ProjectTools-projectField-2yD'):
            creative_fields.append(s_creative_field.css('a::text').get().lower())

        project["creative_fields"] = creative_fields

        tags = []
        for s_tag in response.css('a.ProjectTags-tagLink-Hh_'):
            tags.append(s_tag.css('a::text').get().lower().strip())

        project["tags"] = tags

        self.projects.append(project)


process = CrawlerProcess()

process.crawl(ProjectsSpider)
process.start()