# -*- coding:GBK -*-

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
import scrapy
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class GetLink(BaseSpider):
    name = "getlink"
    allowed_domains = ["china.findlaw.cn"]
    start_urls = ["http://china.findlaw.cn/fagui/area/anhui_hefei/p_1/"]

    area_link = open("../output/area_link.txt", 'a')
    effect_level_link = open("../output/effect_level_link.txt", 'a')

    def parse(self, response):
        response.body.decode('gbk').encode('utf-8')
        sel = Selector(response)

        # 按地区分类的链接
        cityBox_point = sel.xpath('//div[@id="cityBox"]')
        cityBox_context = sel.xpath('//div[@id="cityBox"]/text()').extract()
        cityBox_child_num = len(cityBox_context)

        for i in range(1, cityBox_child_num):
            tmp_point = cityBox_point.xpath('div[' + str(i) + ']/div[1]')
            tmp_context = cityBox_point.xpath('div[' + str(i) + ']/div[1]/text()').extract()
            if len(tmp_context) > 0:
                city_num = len(tmp_context)
                for j in range(1, city_num - 1):
                    city_link = tmp_point.xpath('div[' + str(j) + ']/a[1]/@href').extract()[0]
                    self.area_link.write(city_link + '\n')
                    yield scrapy.Request(city_link, callback=self.parse_area_page)
            else:
                city_link = cityBox_point.xpath('div[' + str(i) + ']/a[1]/@href').extract()[0]
                if city_link != "javascript:void(0);":
                    self.area_link.write(city_link + '\n')
                    yield scrapy.Request(city_link, callback=self.parse_area_page)


        # 按效力分类的链接
        puberBox_point = sel.xpath('//div[@id="puberBox"]')
        puberBox_context = sel.xpath('//div[@id="puberBox"]/text()').extract()
        puberBox_child_num = len(puberBox_context)

        for i in range(1, puberBox_child_num):
            effect_level_link = puberBox_point.xpath('div[' + str(i) + ']/a[1]/@href').extract()[0]
            if effect_level_link != "javascript:void(0);":
                self.effect_level_link.write(effect_level_link + '\n')
                yield scrapy.Request(effect_level_link, callback=self.parse_pub_page)

    def parse_area_page(self, response):
        # response.body.decode('gbk').encode('utf-8')
        sel = Selector(response)
        paging_point = sel.xpath('//div[@id="fenye"]')
        paging_context = sel.xpath('//div[@id="fenye"]/a')

        a_num = len(paging_context)
        if a_num > 0:
            total_page = int(paging_point.xpath('a[' + str(a_num - 1) + ']/text()').extract()[0])

            url_arrs = response.url.split('area/')
            for i in range(2, total_page):
                callback_url = url_arrs[0] + "area/" + url_arrs[1].split('/')[0] + "/p_" + str(i)
                self.area_link.write(callback_url + '\n')
                # print callback_url

    def parse_pub_page(self, response):
        # response.body.decode('gbk').encode('utf-8')
        sel = Selector(response)
        paging_point = sel.xpath('//div[@id="fenye"]')
        paging_context = sel.xpath('//div[@id="fenye"]/a')

        a_num = len(paging_context)
        if a_num > 0:
            total_page = int(paging_point.xpath('a[' + str(a_num - 1) + ']/text()').extract()[0])

            url_arrs = response.url.split('pub/')
            for i in range(2, total_page):
                callback_url = url_arrs[0] + "pub/" + url_arrs[1].split('/')[0] + "/p_" + str(i)
                self.effect_level_link.write(callback_url + '\n')