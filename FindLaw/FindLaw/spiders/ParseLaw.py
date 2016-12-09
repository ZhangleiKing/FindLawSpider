# -*- coding:GBK -*-

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from FindLaw.items import FindlawItem
from FindLaw.items import FindLawPageItem
from pybloomfilter import BloomFilter
from FindLaw.util.JsonParse import JsonParse
import os
import scrapy
import sys
import re

reload(sys)
sys.setdefaultencoding("utf-8")


class ParseLaw(BaseSpider):
    name = "parselaw"
    allowed_domains = ["china.findlaw.cn"]
    start_urls = []

    area_link_file = open('../output/area_link.txt', 'r')
    effect_level_link_file = open('../output/effect_level_link.txt', 'r')

    pubJsonParse = JsonParse('../resources/pub.json')
    provinceJsonParse = JsonParse('../resources/province.json')
    cityJsonParse = JsonParse('../resources/city.json')

    bloom_file_name = 'BloomFilter.bloom'
    bf = None

    item = FindlawItem()

    def __init__(self):
        # ��ʼ��
        self.item['name'] = ""
        self.item['promulgation_unit'] = ""
        self.item['document_number'] = ""
        self.item['date_of_issue'] = None
        self.item['execution_date'] = None
        self.item['timeliness'] = ""
        self.item['effect_level'] = ""
        self.item['content'] = ""
        self.item['content_tag'] = ""
        self.item['url'] = ""
        self.item['type'] = ""
        self.item['province'] = ""
        self.item['city'] = ""
        self.item['pub'] = ""

        bloom_file_exist = os.path.exists(self.bloom_file_name)
        if bloom_file_exist:
            self.bf = BloomFilter.open(self.bloom_file_name)
            print "-----bloomfilter file exist-----"
        else:
            self.bf = BloomFilter(capacity=300000, error_rate=0.0001, filename=self.bloom_file_name)
            print "-----create bloomfilter file -----"

    def start_requests(self):
        try:
            for areaLink in self.area_link_file:
                self.start_urls.append(areaLink.strip())
            for effectLink in self.effect_level_link_file:
                self.start_urls.append(effectLink.strip())

            for url in self.start_urls:
                yield self.make_requests_from_url(url)

        finally:
            self.area_link_file.close()
            self.effect_level_link_file.close()

    def parse(self, response):
        response.body.decode('gbk').encode('utf-8')
        sel = Selector(response)

        item = FindLawPageItem()
        item['type'] = ""
        item['province'] = ""
        item['city'] = ""
        item['pub'] = ""

        item['type'] = self.get_classification(response.url)
        if item['type'] == "����":
            address = response.url.split('area/')[1].split('/')[0]
            address_arr = address.split('_')
            if len(address_arr) > 1:
                province = address_arr[0].lower()
                city = address_arr[1].lower()
                if province == "shanxi":
                    item['province'] = self.get_province_similar(province, city)
                else:
                    item['province'] = self.get_province(province)
                item['city'] = self.get_city(city)
            elif len(address_arr) == 1:
                province = address.lower()
                item['province'] = self.get_province(province)
        else:
            pub_code = response.url.split('pub/')[1].split('/')[0]
            item['pub'] = self.get_pub(pub_code)

        ul_list_point = sel.xpath('//ul[@class="aside-info-listbox-ul"]')
        li_num = len(ul_list_point.xpath('li'))

        for i in range(1, li_num):
            callback_url = ul_list_point.xpath('li[' + str(i) + ']/a/@href').extract()[0]
            # ���bloomfilter�ļ��в�������Ҫ��ȡ��url����Ը�url������ȡ
            if self.bf.__contains__(callback_url) is False:
                yield scrapy.Request(callback_url, meta={'type': item['type'], 'province': item['province'],
                                                         'city': item['city'], 'pub': item['pub']}, callback=self.parse_law)

    def parse_law(self, response):
        self.item['type'] = response.meta['type'].decode('GBK').encode('utf-8')
        self.item['province'] = response.meta['province']
        self.item['city'] = response.meta['city']
        self.item['pub'] = response.meta['pub']

        response.body.decode('gbk').encode('utf-8')
        sel = Selector(response)

        main_body_point = sel.xpath('//div[@id="allPrintContent"]')
        primary_info_point = main_body_point.xpath('div[@class="art-info-table"]')
        content_info_point = main_body_point.xpath('div[@class="art-info"]')
        name_point = main_body_point.xpath('h1')

        self.item['url'] = response.url
        if len(name_point) > 0:
            self.item['name'] = name_point.xpath('text()').extract()[0].strip()

        if len(primary_info_point) == 0:
            possible_time_point = main_body_point.xpath('div[1]')
            possible_time_point_context = possible_time_point.xpath('text()').extract()[0].strip()
            if possible_time_point_context[0:3] == "ʱ�䣺":
                self.item['date_of_issue'] = possible_time_point_context[3:].strip()

        promulgation_unit_point = primary_info_point.xpath('table/tr[1]/td[1]/span[2]/a')
        if len(promulgation_unit_point) > 0:
            self.item['promulgation_unit'] = promulgation_unit_point.xpath('text()').extract()[0].strip()

        document_number_point = primary_info_point.xpath('table/tr[1]/td[2]')
        if len(document_number_point) > 0:
            self.item['document_number'] = document_number_point.xpath('text()').extract()[0][3:67].strip()

        date_of_issue_point = primary_info_point.xpath('table/tr[2]/td[1]')
        if len(date_of_issue_point) > 0:
            self.item['date_of_issue'] = date_of_issue_point.xpath('text()').extract()[0][5:].strip()

        execution_date_point = primary_info_point.xpath('table/tr[2]/td[2]')
        if len(execution_date_point) > 0:
            self.item['execution_date'] = execution_date_point.xpath('text()').extract()[0][5:].strip()

        timeliness_point = primary_info_point.xpath('table/tr[3]/td[1]')
        if len(timeliness_point) > 0:
            self.item['timeliness'] = timeliness_point.xpath('text()').extract()[0][6:].strip()

        effect_level_point = primary_info_point.xpath('table/tr[3]/td[2]')
        if len(effect_level_point) > 0:
            self.item['effect_level'] = effect_level_point.xpath('text()').extract()[0][5:].strip()

        content = ""
        for p_content in content_info_point.xpath('p'):
            content = content + p_content.xpath('descendant::text()').extract()[0].strip() + '\n'
        self.item['content'] = self.filter_tags(content)

        content_tag = "<div>\n"
        p_content_num = len(content_info_point.xpath('p'))
        for i in range(1, p_content_num + 1):
            tmp = content_info_point.xpath('p[' + str(i) + ']')
            if len(tmp) > 0:
                content_tag = content_tag + tmp.extract()[0] + '\n'
        content_tag += "</div>"
        self.item['content_tag'] = content_tag

        # print "name: " + item['name']
        # print "promulgation_unit: " + item['promulgation_unit']
        # print "document_number: " + item['document_number']
        # print "date_of_issue: " + item['date_of_issue']
        # print "execution_date: " + item['execution_date']
        # print "timeliness: " + item['timeliness']
        # print "effect_level: " + item['effect_level']

        yield self.item

    # ��ȡ���࣬�ǰ��յ������࣬����Ч���㼶����
    # ����ֵΪurl
    @staticmethod
    def get_classification(str_url):
        arr = str_url.split("fagui/")
        classification = arr[1].split('/')[0]
        classification_zh = ""
        if classification == "area":
            classification_zh = "����"
        elif classification == "pub":
            classification_zh = "Ч������"

        return classification_zh

    # ���ݴ����Ч���㼶���룬��ȡ�����Ч���㼶
    def get_pub(self, pub_code):
        return self.pubJsonParse.get_pub_by_code(pub_code)

    # ���ݴ����ʡ��ƴ����ȡʡ��
    def get_province(self, province_pinyin):
            return self.provinceJsonParse.get_province_by_pinyin(province_pinyin)

    # ���ݴ���ĳ���ƴ����ȡ����
    def get_city(self, city_pinyin):
        return self.cityJsonParse.get_city_by_pinyin(city_pinyin)

    # ����������ɽ��������ʡ�ݣ�����ƴ��һ��ʱ����Ҫ����������������
    @staticmethod
    def get_province_similar(province_pinyin, city_pinyin):
        # ɽ��
        shanxi_cities = ['taiyuan', 'datong', 'yangquan', 'changzhi', 'jincheng', 'shuozhou', 'jinzhong', 'yuncheng',
                         'xinzhou', 'linfen', 'lvliang']
        # ����
        shanxi2_cities = ['xian', 'baoji', 'xianyang', 'weinan', 'tongchuan', 'yanan', 'yulin', 'ankang', 'hanzhong',
                          'shangluo']
        if province_pinyin == 'shanxi':
            if city_pinyin in shanxi_cities:
                return "ɽ��".decode('GBK').encode('utf-8')
            elif city_pinyin in shanxi2_cities:
                return "����".decode('GBK').encode('utf-8')
            else:
                return "ɽ��/����".decode('GBK').encode('utf-8')

    def replace_char_entity(self, htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ', 'lt': '<', '60': '<', 'gt': '>', '62': '>', 'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entityȫ�ƣ���>
            key = sz.group('name')  # ȥ��&;��entity,��>Ϊgt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # �Կմ�����
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    def filter_tags(self, htmlstr):
        # �ȹ���CDATA
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # ƥ��CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')  # ������
        re_h = re.compile('</?\w+[^>]*>')  # HTML��ǩ
        re_comment = re.compile('<!--[^>]*-->')  # HTMLע��
        re_xml = re.compile('<\?xml[^>]*/>')  # <?XML>ע��
        s = re_cdata.sub('', htmlstr)  # ȥ��CDATA
        s = re_script.sub('', s)  # ȥ��SCRIPT
        s = re_style.sub('', s)  # ȥ��style
        s = re_br.sub('\n', s)  # ��brת��Ϊ����
        s = re_h.sub('', s)  # ȥ��HTML ��ǩ
        s = re_comment.sub('', s)  # ȥ��HTMLע��
        s = re_xml.sub('', s)
        # ȥ������Ŀ���
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = self.replace_char_entity(s)  # �滻ʵ��
        return s

    def repalce(self, re_exp, repl_string):
        return re_exp.sub(repl_string, self)




