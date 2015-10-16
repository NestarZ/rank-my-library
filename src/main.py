#!/usr/bin/python
# -*- coding: "utf-8"-*-

import requests
import os
import json
import time
import re
import sys
import csv_maker
import pick_best_data

class Master(object):
    def __init__(self):
        time_id = str(time.strftime("%m%Y"))
        api_dic = self.load_apis()
        self.scanner = RankMyLibrary(time_id, api_dic)

    def run(self):
        args = sys.argv + [0]*5
        if "--movie" in args or "--all" in args or not("--movie" in args or "--anime" in args):
            movie_folder = os.listdir("/media/nestarz/Disque local1/Videos/Films")
            self.scanner.scan(movie_folder, "movie")
        if "--anime" in args or "--all" in args or not("--movie" in args and "--anime" in args):
            animes_folder1 = os.listdir("/media/nestarz/Disque local1/Videos/Animes/Series d'animation")
            animes_folder2 = os.listdir("/media/nestarz/Disque local/Videos/Animes/Series d'animation")
            animes_folder3 = os.listdir("/media/nestarz/8AB2AF54B2AF4413/Videos/Animes/Series d'animation")
            animes_folders = animes_folder1 + animes_folder2 + animes_folder3
            self.scanner.scan(animes_folders, "anime")

    def load_apis(self):
        file_dir = os.path.dirname(os.path.realpath(__file__))
        with open(file_dir+"/../api/list_api.json",'r') as f:
            data = json.load(f)
        apis = {}
        for content_type in data.keys():
            apis[content_type] = []
            for name, api in data[content_type].items():
                apis[content_type].append(API(name, content_type, api))
        return apis

class API(object):
    def __init__(self, api_name, api_type, data):
        self.name = api_name
        self.api_type = api_type
        self.data = data

    def get_url(self, title, year=''):
        url = "{}{}?{}={}&{}={}"
        return url.format(self.data["url"],
                    self.data["endpoint"],
                    self.data["parameters"]["search_bytitle"],
                    title,
                    self.data["parameters"].get("search_byyear", ''),
                    year)

class Content(object):
    def __init__(self, ctype, name, api, data={}):
        self.content_type = ctype
        self.name = name
        self.api = api
        self.data = data

    def json_parse(self):
        jp = {key:str(self.data[v]) if v else "" for key, v in self.api.data["metadata"].items()}
        jp.update({"api_name":self.api.name, "dir":self.name, "type":self.content_type})
        return jp

    @classmethod
    def fromJson(cls, data):
        return Content(data["type"], data["dir"], data["api_name"], data)

class RankMyLibrary(object):
    def __init__(self, time_id, api_dic):
        self.time_id = time_id
        self.api_dic = api_dic

    def get(self, url):
        return requests.get(url)

    def find_in_api(self, api, content_type, name):
        cname = re.sub(r'\([^)]*\)', '', name).rstrip().lstrip()
        print(api.get_url(cname))
        response = self.get(api.get_url(cname))
        data = {}
        if response.status_code == 200:
            data = json.loads(response.text)
        if isinstance(data, dict) and data and data.get("Response","True") == "True":
            return Content(content_type, name, api, data)
        elif isinstance(data, list):
            data = pick_best_data.pick_best(name, api, data)
            return Content(content_type, name, api, data)

    def find_in_json(self, api_name, data, name):
        for content in data:
            if name in content.values() and content["api_name"] == api_name:
                print('| {} ({})'.format(name, api_name))
                return Content.fromJson(content)

    def get_json(self, fname):
        if not os.path.isfile(fname):
            with open(fname,'w') as f:
                json.dump([], f)
        with open(fname,'r') as f:
            return json.load(f)

    def update_json(self, fname, data, content):
        with open(fname,'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            print('+ {} ({})'.format(content.name, content.api.name))

    def update_csv(self, fname, data):
        csv_maker.doCSV(fname, data)

    def scan(self, folders, content_type):
        file_dir = os.path.dirname(os.path.realpath(__file__))
        fname = file_dir+"/../data/{}_{}".format(content_type,self.time_id)
        csv_ext, json_ext = ".csv", ".json"
        data = self.get_json(fname+json_ext)
        for api in self.api_dic.get(content_type, self.api_dic["divers"]):
            print(api.name)
            if (api.name) == "myapifilms_imdb": continue
            for folder in folders:
                content = self.find_in_json(api.name, data, folder)
                if not content:
                    content = self.find_in_api(api, content_type, folder)
                    if not content:
                        continue
                    data.append(content.json_parse())
                    self.update_json(fname+json_ext, data, content)
                    self.update_csv(fname+csv_ext, data)

if __name__=="__main__":
    m = Master()
    m.run()
