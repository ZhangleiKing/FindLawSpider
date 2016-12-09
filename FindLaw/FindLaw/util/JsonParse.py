# -*- coding:utf-8 -*-
import json
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class JsonParse(object):
    json_content = None

    def __init__(self, json_file_name):
        json_file = file(json_file_name)
        self.json_content = json.load(json_file)

    # 根据城市拼音获取城市名称
    def get_city_by_pinyin(self, city_pinyin):
        for city in self.json_content['chineseCities']:
            if city_pinyin == city['pinyin'].lower():
                return city['name']
        return "未知城市"

    # 根据省份拼音获取省份名称
    def get_province_by_pinyin(self, province_pinyin):
        for province in self.json_content['chineseProvinces']:
            if province_pinyin == province['pinyin'].lower():
                return province['name']
        return "未知省份"

    # 根据效力层级代码号来获取效力层级
    def get_pub_by_code(self, pub_code):
        for pubs in self.json_content['pubs']:
            if pub_code == pubs['code']:
                return pubs['name']
        return "未知效力层级"

    def print_all(self):
        for city in self.json_content['chineseCities']:
            print city['name'] + ' ' + city['pinyin']