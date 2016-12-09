# -*- coding:GBK -*-

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
import scrapy
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


#该类已无效，所有的功能写至GetLink类
class ValidAreaLink(BaseSpider):
    name = "valid_area_link"
    allowed_domains = ["china.findlaw.cn"]
    start_urls = []

    area_link = open("../output/area_link.txt", 'a')

    def start_requests(self):
        # try:
        #     for single_link in self.area_link:
        #         self.start_urls.append(single_link.strip())
        #     for url in self.start_urls:
        #         yield self.make_requests_from_url(url)
        #
        # finally:
        #     self.area_link.close()

        url = "http://china.findlaw.cn/fagui/area/anhui_hefei/p_6/"
        self.start_urls.append(url)
        for url in self.start_urls:
                yield self.make_requests_from_url(url)

    def parse(self, response):
        response.body.decode('gbk').encode('utf-8')
        sel = Selector(response)

        # list_ul_point = sel.xpath('//ul[@class="aside-info-listbox-ul"]')
        # list_ul_context = sel.xpath('//ul[@class="aside-info-listbox-ul"]/li').extract()
        #
        # li_num = len(list_ul_context)
        #
        # for i in range(1, li_num):
        #     file_link = list_ul_point.xpath('li[' + str(i) +']/a/@href')
        #     self.area_file_link.write(file_link + '\n')

        paging_point = sel.xpath('//div[@id="fenye"]')
        paging_context = sel.xpath('//div[@id="fenye"]/a')

        a_num = len(paging_context)

        total_page = paging_point.xpath('a[' + str(a_num-1) + ']/text()').extract()[0]

        print "num: "+str(len(paging_context))
        print total_page

        url_arrs = response.url.split('area/')
        callback_url = url_arrs[0] + "area/" + url_arrs[1].split('/')[0] + "/p_" +str(total_page)
        print callback_url
