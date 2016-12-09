# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class FindlawItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 爬取的页面url
    url = Field()

    # 法律法规名称
    name = Field()

    # 颁布单位
    promulgation_unit = Field()

    # 文号
    document_number = Field()

    # 颁布日期
    date_of_issue = Field()

    # 执行日期
    execution_date = Field()

    # 时效性
    timeliness = Field()

    # 效力级别
    effect_level = Field()

    # 正文
    content = Field()

    # 带标签的正文
    content_tag = Field()

    # 分类（地区、效力层级）
    type = Field()

    # 省份
    province = Field()

    # 城市
    city = Field()

    # 具体效力层级
    pub = Field()

    pass


class FindLawPageItem(Item):
    # 分类（地区、效力层级）
    type = Field()

    # 省份
    province = Field()

    # 城市
    city = Field()

    # 具体效力层级
    pub = Field()

    pass
