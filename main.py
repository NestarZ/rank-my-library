#!/usr/bin/python
# -*- coding: "utf-8"-*-

import requests
import os
import json

ANIME = {"myanimelist": "http://myanimelist.net/anime.php?q="}
ALL = {"omdb": "http://www.omdbapi.com/?", "myapifilms_imdb": "http://www.myapifilms.com/imdb?"}
FOLDERS =  os.listdir("/media/nestarz/Disque local1/Videos/Animes/Series d'animation")

def get(url):
    return requests.get(url)#, auth=('Necka', 'energy33'))

def find(api_name, name):
    url = ALL[api_name]
    params = 'title={}'.format(name) + '&data=S' + '&format=JSON'
    response = get('{}{}'.format(url, params))
    data = json.loads(response.text, 'utf-8')
    with open('data.md','a') as f:
        f.write("\n### {}\n".format(name))
        f.write("\n##### {}\n".format(api_name))
    if isinstance(data, dict) and data.get("code", -1) == 110:
        with open('data.md','a') as f:
            f.write("*Not found*")
        print("{:5} not found on {}".format(name, url))
        return {'dir':name, 'title':'', 'year':'', 'rating':'', 'genres':['']}
    data = data[0]
    title, year, rating, genres = data["title"], data["year"], data["rating"], data["genres"]
    print(title, year, rating)
    with open('data.md','a') as f:
        a = '- **Title** : {},\n- **Year** : {},\n- **Rating** : {}\n\n'.format(title, year, rating)
        f.write(a)
    return {'dir':name, 'title':title, 'year':year, 'rating':rating, 'genres':genres}

with open('data.md','w') as f:
    pass
with open('data.json','w') as f:
    pass
info = []
for folder in FOLDERS:
    if not '.' in folder:
        info.append(find("myapifilms_imdb", folder))
        print(info[-1])
with open('data.json','a') as f:
    json.dump(info, f)
