#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Project ：grammarCheckerbasedOpenai 
@File ：Config.py
@Author ：HuntingGame
@Date ：2023-06-11 9:33 
C'est la vie!!! enjoy ur day :D
'''


import json

class ConfigReader:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigReader, cls).__new__(cls)
        return cls._instance

    def __init__(self,path,partten="EWA"):
        self.path = path
        self.config = {"prompt":""}
        self.partten=partten
        self.load_config(path)

    def load_config(self,path):
        try:
            with open(path) as file:
                self.config = json.load(file)[self.partten]
            with open(path.split("/")[0] +"/" +  self.config["prompt_path"],'r',encoding='utf-8') as f:
                self.config["prompt"] = f.read()
                #print(self.config["prompt"])

        except FileNotFoundError:
            print("config.json or prompt file not found.")
            if "prompt" not in self.config:
                self.config["prompt"] = ""
    def get_value(self, key):
        return self.config.get(key)







if __name__ == "__main__":
    # Usage example
    config_reader = ConfigReader("config/config.json","EWA")
    value = config_reader.get_value("max_token")
    print(value)
    print(config_reader.get_value("isAutoCopy"))