#!/usr/bin/python
# -*- coding: "utf-8"-*-

import requests
import os
import json
import time
import csv
import re

TIME_ID = str(time.strftime("%m%Y"))
ANIME_API = {"hummingbirdv1": "https://hummingbird.me/api/v1/search/anime/?"}
DIVERS_API = {"netflix": "http://netflixroulette.net/api/api.php?", "omdb": "http://www.omdbapi.com/?", "myapifilms_imdb": "http://www.myapifilms.com/imdb?"}
API = {"anime": dict(ANIME_API, **{}), "movie": DIVERS_API}

class Content(object):
    def __init__(self, ctype, name, api_name='', data={}):
        if api_name == "hummingbirdv1":
            done = False
            maxb = 3
            best = data[0]
            if not(best['title'].encode('utf-8').lower() == name.lower() or best['title'].encode('utf-8') == name.lower()):
                for e in data:
                    if not e['alternate_title']:
                        e['alternate_title'] = ""
                    for j in reversed(range(maxb,len(name))):
                        for k in range(0,len(name),j):
                            if k+j<len(name) and (name[k:k+j+1].lower() in e['title'].encode('utf-8').lower() or name[k:k+j+1].lower() in e['alternate_title'].encode('utf-8').lower()):
                                if j > maxb:
                                    maxb, best = j, e
                                break
            data = best
        data = lower_keys(data)
        self.content_type = ctype
        self.name = name
        self.title = data.get("title", data.get("show_title", ""))
        self.year = data.get("year",  data.get("release_year", ""))
        self.rating = data.get("imdbrating", data.get("metascore", data.get("rating", "")))
        self.genres = data.get("genres", data.get("genre", data.get("category",[""])))
        self.plot = data.get("plot", data.get("summary",""))
        self.api_name = api_name

    def json_parse(self):
        return {"type":self.content_type,
                "dir":self.name,
                "title":self.title,
                "year":self.year,
                "rating":self.rating,
                "genres":self.genres,
                "api_name":self.api_name,
                "plot":self.plot}

    @classmethod
    def create(cls, content_type, *args):
        Content_type = find_type(content_type)
        return Content_type(*args)

    @classmethod
    def fromJson(cls, data):
        return Content.create(data["type"], data["dir"], data)

class Anime(Content):
    def __init__(self, *args):
        Content.__init__(self, "anime", *args)

class Movie(Content):
    def __init__(self, *args):
        Content.__init__(self, "movie", *args)

def lower_keys(data):
    return dict((k.lower(), v) for k,v in data.iteritems())

def doCSV(csv_file_path, raw_data):
    def reduce_item(key, value):
        #Reduction Condition 1
        if type(value) is list:
            if type(value[0]) is str:
                reduced_item[str(key)] = ', '.join(value)
            elif type(value[0]) is dict:
                reduced_item[str(key)] = ""
                for sub_item in value[:-1]:
                    reduced_item[str(key)] += ', '.join(sub_item.values()) + ', '
                reduced_item[str(key)] += ', '.join(value[-1].values())

        #Reduction Condition 2
        elif type(value) is dict:
            sub_keys = value.keys()
            for sub_key in sub_keys:
                reduce_item(key+'_'+str(sub_key), value[sub_key])

        #Base Condition
        else:
            reduced_item[str(key)] = value.encode('utf-8')
    processed_data = []
    header = []
    for item in raw_data:
        reduced_item = {}
        reduce_item('', item)

        header += reduced_item.keys()

        processed_data.append(reduced_item)

    header = list(set(header))
    header.sort()

    with open(csv_file_path, 'wb+') as f:
        writer = csv.DictWriter(f, header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in processed_data:
            writer.writerow(row)

def get(url):
    return requests.get(url)#, auth=('Necka', 'energy33'))

def find_type(content_type):
    types = {"anime": Anime, "movie": Movie}
    return types[content_type]

def find_in_api(api_name, url, content_type, name):
    Content_type = find_type(content_type)
    cname = re.sub(r'\([^)]*\)', '', name).rstrip().lstrip()
    params = 'title={}'.format(cname) + '&data=S' + '&r=json'+ '&t={}'.format(cname) + '&query={}'.format(cname)
    response = get('{}{}'.format(url, params))
    try:
        data = json.loads(response.text, 'utf-8')
    except:
        return None
    return Content_type(name, api_name, data)

def find_in_json(api_name, data, name):
    for content in data:
        if name.decode('utf-8') in content.values() and content["api_name"] == api_name:
            print('| {} ({})'.format(name, api_name))
            return Content.fromJson(content)

def get_json(fname):
    if not os.path.isfile(fname):
        with open(fname,'w') as f:
            json.dump([], f)
    with open(fname,'r') as f:
        return json.load(f)

def update_json(fname, data, content):
    with open(fname,'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)
        print('+ {} ({})'.format(content.name, content.api_name))

def update_csv(fname, data):
    doCSV(fname, data)

def scan(folders, content_type):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    fname = file_dir+"/../data/{}_{}".format(content_type,TIME_ID)
    csv_ext, json_ext = ".csv", ".json"
    data = get_json(fname+json_ext)
    for api_name, url in API[content_type].items():
        for folder in folders:
            content = find_in_json(api_name, data, folder)
            if not content:
                content = find_in_api(api_name, url, content_type, folder)
                if not content:
                    continue
                data.append(content.json_parse())
                update_json(fname+json_ext, data, content)
                update_csv(fname+csv_ext, data)

if __name__ == "__main__":
    import sys
    args = sys.argv + [0]*5
    if "--movie" in args or "--all" in args or not("--movie" in args or "--anime" in args):
        movie_folder = os.listdir("/media/nestarz/Disque local/Videos/Films")
        scan(movie_folder, "movie")
    if "--anime" in args or "--all" in args or not("--movie" in args and "--anime" in args):
        animes_folder1 = os.listdir("/media/nestarz/Disque local1/Videos/Animes/Series d'animation")
        animes_folder2 = os.listdir("/media/nestarz/Disque local/Videos/Animes/Series d'animation")
        animes_folder3 = os.listdir("/media/nestarz/8AB2AF54B2AF4413/Videos/Animes/Series d'animation")
        animes_folders = animes_folder1 + animes_folder2 + animes_folder3
        scan(animes_folders, "anime")
