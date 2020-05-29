import requests
from bs4 import BeautifulSoup
import json
import dumper

import json
import inspect

class ObjectEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj

class Author(object):
    name = ""
    
    _link = ""

class Stats(object):
    views = 0
    comments = 0
    appreciations = 0

class Project(object):
    name = ""
    platform = ""

    views = 0
    comments = 0
    appreciations = 0

    tags = []

    author_name = ""
    author_link = ""

    _link = ""


def get_dribbble_projects(keyword):
    projects_list = []

    URL = 'https://dribbble.com/search/' + keyword
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    projects = soup.findAll('li', class_='shot-thumbnail-with-hover-overlay')

    for project in projects:
        p = Project()
        p.platform = "Dribbble"
        p.name = project.find('p', class_='shot-title').contents[0]
        p._link = f"https://dribbble.com/{project['data-screenshot-id']}"

        p.appreciations = int(project.find('li', class_='fav').find('span').contents[0])
        p.comments = int(project.find('li', class_='cmnt').find('span').contents[0])

        try:
            p.author_name = project.find('span', class_='display-name').contents[0]
            p.author_link = 'https://dribbble.com' + project.find('a', class_='hoverable url')["href"]
        except:
            pass

        projects_list.append(p)

    return projects_list

def get_behance_projects(keyword):
    projects_list = []

    URL = 'https://www.behance.net/search?search=' + keyword
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    projects = soup.findAll('li', class_='ContentGrid-gridItem-2Ad qa-grid-item')

    for project in projects:
        p = Project()
        p.platform = "Behance"
        p.name = project.find('a', class_='qa-title-owner').contents[0]
        p._link = project.find('a', class_='js-project-link')["href"]

        p.appreciations = project.find('div', class_='Stats-stats-1iI').getText().split()[0]
        # p.views = project.find('div', class_='Stats-stats-1iI').getText().split()[1]
        p.tags = get_project_tags(p._link)

        try:
            p.author_name = project.find('a', class_='OwnersNeue-owner-3CC').getText()
            p.author_link = project.find('a', class_='OwnersNeue-owner-3CC')["href"]
        except:
            pass

        projects_list.append(p)

    return projects_list

def get_text(elem):
    if elem is not None:
        return elem.getText()
    else:
        return ""

def get_attr(elem, attr):
    if elem is not None:
        return elem[attr]
    else:
        return ""

def get_user_info(link):
    stats = {}

    user = {
        "_link": link,
        "avatar": "TBD"
    }

    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    user["avatar"] = get_attr(soup.find('img', class_='AvatarImage-avatarImage-3uu'), 'src')
    user["name"] = get_text(soup.find('h1', class_='Profile-userFullName-_EP'))
    user["position"] = get_text(soup.find('p', class_='Profile-line-2Cz'))

    s_stats = soup.findAll('a', class_='UserInfo-statValue-1_-')
    stats["project_views"] = int(get_text(s_stats[0]).replace(',', ''))
    stats["appreciations"] = int(get_text(s_stats[1]).replace(',', ''))
    stats["followers"] = int(get_text(s_stats[2]).replace(',', ''))
    stats["following"] = int(get_text(s_stats[3]).replace(',', ''))

    s_project_links = soup.findAll('a', 'ProjectCoverNeue-coverLink-102')
    projects = []
    # for s_project_link in s_project_links:
    #     projects.append(get_project_info(s_project_link["href"]))

    user["stats"] = stats
    user["projects"] = projects

    return user

    

def get_project_info(link):
    project = {
        "id": 0,
        "_link": link
    }

    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    project["title"] = get_text(soup.find('span', "Project-title-18X"))

    creative_fields = []
    for s_creative_field in soup.findAll('a', class_="ProjectTools-projectFieldLink-3rc"):
        creative_fields.append(get_text(s_creative_field).lower())

    project["creative_fields"] = creative_fields

    tags = []
    for s_tag in soup.findAll('li', class_='ProjectTags-tag-En-'):
        tags.append(get_text(s_tag).lower().strip())

    project["tags"] = tags

    # s_tags = 
    # for tg in s_tags:
    #     tags.append(tg.getText().strip().lower())
    
    return project

# projects = get_behance_projects('dashboard')
# projects += get_dribbble_projects('dashboard')

# open('projects.json', 'w').write(json.dumps(projects, cls=ObjectEncoder, indent=4))

# print(get_project_tags("https://www.behance.net/gallery/93948913/Interface-Dashboard-v2?tracking_source=search_projects_recommended%7Cdashboard"))

# print(json.dumps(get_user_info("https://www.behance.net/marinazabolot/projects"), indent=4))

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
import io

class ProjectsSpider(scrapy.Spider):
    name = "projects"
    urls = [
        "https://www.behance.net/gallery/96577957/Coronavirus-hygiene-note-%28poster%29",
        "https://www.behance.net/gallery/95874069/stroitelnye-raboty"
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
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        project = {}

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