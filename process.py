import json
import csv
import re
import math

from collections import Counter

nodes_file = open('nodes.csv', 'w', newline='')
edges_file = open('edges.csv', 'w', newline='')

users = json.load(open("users.json"))
projects = json.load(open("projects.json"))

nodes_writer = csv.DictWriter(nodes_file, fieldnames=['id', 'label', 'creative_fields'])
edges_writer = csv.DictWriter(edges_file, fieldnames=['source', 'target', 'type', 'weight'])

nodes_writer.writeheader()
edges_writer.writeheader()

def get_project_tags(user):
    tags = []

    for project_id in user["projects"]:
        project = next(filter(lambda project: project['id'] == project_id["id"], projects), None)
        tags.extend(project["creative_fields"])

    return tags

def get_score(user1, user2):
    tags1 = Counter(get_project_tags(user1))
    tags2 = Counter(get_project_tags(user2))

    return counter_cosine_similarity(tags1, tags2)

def counter_cosine_similarity(c1, c2):
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))

    return dotprod / (magA * magB)

for user in users:
    nodes_writer.writerow(
        {
            'creative_fields': ', '.join(list(set(get_project_tags(user)))),
            'id': user['username'],
            'label': re.sub('[^A-Za-z0-9]+', '', user['name'])
        }
    )

for user1 in users:
    for user2 in users:
        if user1["username"] != user2["username"]:
            score = get_score(user1, user2)

            if score > 0.2:
                edges_writer.writerow(
                    {
                        'source': user1["username"],
                        'target': user2["username"],
                        'type': "undirected",
                        "weight": score
                    }
                )
