# -*- coding: utf-8 -*-
import re
import scrapy
import json
import random

from Maimai.items import BaseItem
from Maimai.items import WorkItem
from Maimai.items import EduItem
from Maimai.items import CommentItem
from Maimai.settings import MYSQL_CONFIG
from Maimai.spiders.cookie import other_cookies
from Maimai.mysqlpipelines.sql import Sql

MYSQL_HOST = MYSQL_CONFIG['MYSQL_HOST']
MYSQL_USER = MYSQL_CONFIG['MYSQL_USER']
MYSQL_PASSWD = MYSQL_CONFIG['MYSQL_PASSWD']
MYSQL_PORT = MYSQL_CONFIG['MYSQL_PORT']
MYSQL_DB = MYSQL_CONFIG['MYSQL_DB']

# 往redis数据库中存放一个开始的encode_mmid
Sql.push_new_encode_mmid('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
                         'eyJ1IjozMTUzNywibGV2ZWwiOjAsInQiOiJjd'
                         'HQifQ.SCEVL0s7GT_pOvSRCVROcaNRurS-fUb'
                         'NTGnEquQRM2I', 31537)
# COOKIE
COOKIES = other_cookies

NONE_STR = lambda x: '' if x == 'None' else str(x)

WORK_END_DATE = lambda x: '至今' if x == 'None' else x

SEX_DICT = {
    u'他': '男',
    u'她': '女',
}

DEGREE_DICT = {
    0: '专科',
    1: '本科',
    2: '硕士',
    3: '博士',
    4: '博士后',
    5: '其他',
    255: '其他',
}


class MaimaiSpider(scrapy.Spider):
    name = 'maimai'
    allowed_domains = ['maimai.cn', ]
    start_urls = ['http://maimai.cn/', ]

    head_url = 'https://maimai.cn/company/contacts?count='
    page_url = '&page='
    cid_url = '&cid='
    json_url = '&jsononly=1'

    friends_url = 'https://maimai.cn/contact/card_lst?type=work_card&stdname={}&u2={}'
    school_url = 'https://maimai.cn/contact/card_lst?type=education_card&stdname={}&u2={}'
    referer = 'https://maimai.cn/contact/detail/{}?from=webview#/company/contacts'
    person_url = 'https://maimai.cn/contact/detail/{}/?from=webview%23%2Fcompany%2Fcontacts&jsononly=1'
    comment_url = 'https://maimai.cn/contact/comment_list/{}/?jsononly=1'

    def start_requests(self):
        '''
            从待爬池中获取一个人url 开始爬取
        '''
        try:
            new_mmid = Sql.get_new_encode_mmid()
            if new_mmid:
                new_mmid = new_mmid.split(' :')

                referer = self.referer.format(new_mmid[1])

                person_url = self.person_url.format(new_mmid[0])

                comment_url = self.comment_url.format(new_mmid[0])
                yield scrapy.Request(comment_url, callback=self.get_comment,
                                     headers={'Referer': referer})

                cookies = random.choice(COOKIES)
                yield scrapy.Request(person_url, cookies=cookies,
                                     callback=self.get_info, headers={'Referer': referer})
        except:
            pass

    def parse(self, response):
        pass

    def get_info(self, response):
        """
            解析个人信息
        """
        content = json.loads(response.body)

        try:
            card = content['data']['card']
            uinfo = content['data']['uinfo']
            sex = content['data']['ta']

            # 个人ID
            id = str(card['id'])

            # 基本信息
            item = BaseItem()
            # id
            item['id'] = id
            # url
            item['url'] = response.url
            # 姓名
            item['name'] = card['name']
            # 头像链接
            item['img'] = card['avatar_large']
            # 公司
            item['company'] = card['company']
            # 职位
            item['position'] = card['position']
            # 工作地
            item['work_city'] = card['province'] + '-' + card['city']
            # 性别
            item['sex'] = SEX_DICT.get(sex, '不详')
            # 家乡
            item['birth_city'] = NONE_STR(uinfo.get('ht_province', ' ')) + \
                                 '-' + NONE_STR(uinfo.get('ht_city', ' '))
            if item['birth_city'] == '-':
                item['birth_city'] = ''
            # 星座
            item['xingzuo'] = uinfo.get('xingzuo', '')
            # 生日
            item['birthday'] = NONE_STR(uinfo.get('birthday', ''))
            # 标签
            item['tag'] = ','.join(uinfo['weibo_tags'])
            item['headline'] = uinfo.get('headline', '')
            yield item

            # 工作经历
            for work_exp in uinfo['work_exp']:
                item = WorkItem()
                item['id'] = id
                item['company'] = work_exp['company']
                item['position'] = work_exp['position']
                item['description'] = work_exp.get('description', '')
                item['start_date'] = work_exp['start_date']
                item['end_date'] = WORK_END_DATE(work_exp['end_date'])
                yield item

                # 获取他(她)在本公司的好友
                cookies = random.choice(COOKIES)
                friends_list_url = self.friends_url.format(item['company'], item['id'])
                yield scrapy.Request(friends_list_url,
                                     callback=self.get_encode_mmid,
                                     cookies=cookies,
                                     headers={'Referer': 'https://maimai.cn/'})

            # 教育经历
            for edu_exp in uinfo['education']:
                item = EduItem()
                item['id'] = id
                item['school'] = edu_exp['school']
                item['degree'] = DEGREE_DICT[edu_exp.get('degree', '255')]
                item['department'] = edu_exp['department']
                item['start_date'] = edu_exp['start_date']
                item['end_date'] = edu_exp.get('end_date', '')
                yield item

                # 获取ta校友列表
                cookies = random.choice(COOKIES)
                friends_list_url = self.school_url.format(item['school'], item['id'])
                yield scrapy.Request(friends_list_url,
                                     callback=self.get_encode_mmid,
                                     cookies=cookies,
                                     headers={'Referer': 'https://maimai.cn/'})
        except Exception as e:
            print('====================================================')
            print(e)
            print('====================================================')
            print(response.body.decode())
            print('====================================================')

    def get_comment(self, response):
        """
        获取好友对ta的评价
        :param response: response
        :return: item
        """
        try:
            content = json.loads(response.body)
            comment_list = content['data']['evaluation_list']

            for comment in comment_list:
                item = CommentItem()
                item['id'] = comment['user']['id']
                item['friend_id'] = comment['src_user']['id']
                item['friend_name'] = comment['src_user']['name']
                item['friend_company'] = comment['src_user']['company']
                item['friend_position'] = comment['src_user']['position']
                item['level'] = comment['re']
                item['comment'] = comment['text']
                yield item
        except Exception as e:
            print('====================================================')
            print(e)
            print('====================================================')
            print(response.body)
            print('====================================================')

    # 从同事、校友中获得新的mmid
    def get_encode_mmid(self, response):

        data = re.findall('share_data = JSON.parse\((".+?")\);</script>.*', response.body.decode())[0]

        p = re.compile('null')
        p2 = re.compile('false')
        p3 = re.compile('true')
        data = re.sub(p, 'None', data)
        data = re.sub(p2, 'False', data)
        data = re.sub(p3, 'True', data)

        data = eval(eval(data))

        # 存到redis
        for mmid in data['data']['contacts']:
            if mmid:
                Sql.push_new_encode_mmid(mmid['encode_mmid'], mmid['id'])

        # 开始爬取下一个人
        try:
            new_mmid = Sql.get_new_encode_mmid()
            if new_mmid:
                new_mmid = new_mmid.split(' :')

                referer = self.referer.format(new_mmid[1])

                person_url = self.person_url.format(new_mmid[0])

                comment_url = self.comment_url.format(new_mmid[0])
                yield scrapy.Request(comment_url, callback=self.get_comment,
                                     headers={'Referer': referer})

                cookies = random.choice(COOKIES)
                yield scrapy.Request(person_url, cookies=cookies,
                                     callback=self.get_info, headers={'Referer': referer})
        except:
            pass
