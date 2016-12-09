#coding: utf-8
from FindLaw.settings import PROXIES
import base64
import random
import time
import sys
import threading
reload(sys)
sys.setdefaultencoding("utf-8")

ip_file = open('../resources/ip.txt', 'r')


class ProxyMiddleware(object):

    random_seed = 3
    ip_num = 0
    threads = []
    lines = None
    count = 0

    # def __init__(self):
    #     self.lines = ip_file.readlines()
    #
    #     self.ip_num = len(self.lines)
    #
    #     # t1 = threading.Thread(target=self.time_interval())
    #     # self.threads.append(t1)
    #     #
    #     # for t in self.threads:
    #     #     t.setDaemon(True)
    #     #     t.start()
    #
    # def process_request(self, request, spider):
    #     self.count += 1
    #     if self.count > 1500:
    #         self.random_seed += 1
    #         self.count = 0
    #         if self.random_seed > self.ip_num - 1:
    #             self.random_seed = 1
    #
    #     for line in self.lines[self.random_seed - 1: self.random_seed]:
    #         request.meta['proxy'] = line

    def process_request(self, request, spider):
        lines = ip_file.readlines()
        random_num = 1
        for line in lines[random_num - 1: random_num]:
            request.meta['proxy'] = line

    @staticmethod
    def sleep_time(hour, minute, sec):
        return hour*3600 + minute*60 + sec

    def time_interval(self):
        while True:
            time.sleep(self.sleep_time(0, 0, 30))
            self.random_seed += 1
            if self.random_seed > self.ip_num-1:
                self.random_seed = 1
