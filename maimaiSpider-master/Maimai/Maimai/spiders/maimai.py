# -*- coding: utf-8 -*-
import re

import pymysql
import scrapy
import json
import random
from Maimai.items import BaseItem
from Maimai.items import WorkItem
from Maimai.items import EduItem
from Maimai.items import CommentItem
from Maimai.settings import MYSQL_CONFIG
from Maimai.spiders.cookie import other_cookies_mob

MYSQL_HOST = MYSQL_CONFIG['MYSQL_HOST']
MYSQL_USER = MYSQL_CONFIG['MYSQL_USER']
MYSQL_PASSWD = MYSQL_CONFIG['MYSQL_PASSWD']
MYSQL_PORT = MYSQL_CONFIG['MYSQL_PORT']
MYSQL_DB = MYSQL_CONFIG['MYSQL_DB']

# cnx = pymysql.connect(user=MYSQL_USER, passwd=MYSQL_PASSWD, host=MYSQL_HOST, db=MYSQL_DB, port=MYSQL_PORT,
#                       charset='utf8')
# cur = cnx.cursor()
#
# # 待爬池获取个人信息
# cur.execute('select distinct encode_mmid from simpleitem_search where id not in (select id from baseitem)')
#
# # 指定本次爬去数量
# # rows = cur.fetchall()
# rows = cur.fetchmany(10000)
# rows = cur.fetchmany(10)

# cur.close()

rows = [[
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1Ijo1MjIxOTg1LCJsZXZlbCI6MCwidCI6ImN0dCJ9.f4vfzgn_iAV-8JZwPfywiaF9iidEvWxDeWR6M7NOuUE',
    '5221985'],
]

# COOKIE
COOKIES = other_cookies_mob

NONE_STR = lambda x: '' if x == 'None' else x

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

    def start_requests(self):
        '''
            从待爬池中获取个人url
        '''
        referer_end_url = '?from=webview#/company/contacts'

        start_url = 'https://maimai.cn/contact/detail/'
        end_url = '/?from=webview%23%2Fcompany%2Fcontacts&jsononly=1'


        comment_start_url = 'https://maimai.cn/contact/comment_list/'
        comment_end_url = '/?jsononly=1'

        cookie = {  # taobao2
            'guid': 'HBoEGxMeBBsSHwQYVgcYGxkYHRgSHhIcVhwZBB0ZHwVDWEtMS3kKHhMEGBoYGQQaBBgcBU9HRVhCaQoDRUFJT20KT0FDRgoGZmd+YmECChwZBB0ZHwVeQ2FIT31PRlpaawoDH3UYG3UaGwpyCnllCklLZwpGT15EYwoRQllFXkRDSUtnAgoaBB8FS0ZGQ1BFZw==',
            'koa:sess': 'eyJ1IjoiODkwMzk0NDYiLCJzZWNyZXQiOiJ4WjF5QnRYUUNUN1VTTkluZGsxenY4LW4iLCJtaWQ0NTY4NzYwIjpmYWxzZSwic3RhdHVzIjp0cnVlLCJfZXhwaXJlIjoxNTEyNzIyNTI0MDM1LCJfbWF4QWdlIjo4NjQwMDAwMH0=',
            'koa:sess.sig': 'oaXVIawsPvQRzR9Wy9Y1XTIo8FQ',
            'seid': 's1512635328665',
            'token': '"nUvvJ8vGUXMgr6XK2BxcUds2IGswDcnAwwMUFTwAEYlzG3rj1rqSJb2Qn/CxHKpa8CKuzcDfAvoCmBm7+jVysA=="',
            'uid': '"N+h84R9cntB6AqDgPfAx5/Airs3A3wL6ApgZu/o1crA="'
        }

        for row in rows:
            referer = start_url + row[1] + referer_end_url

            # 评价
            comment_url = comment_start_url + row[0] + comment_end_url
            yield scrapy.Request(comment_url, callback=self.get_comment, cookies=cookie, headers={'Referer': referer})

            # 个人信息
            person_url = start_url + row[0] + end_url
            # 使用不同cookie，模拟手机或网页请求
            cookies = random.choice(COOKIES)
            yield scrapy.Request(person_url, cookies=cookie, callback=self.get_info, headers={'Referer': referer})



    def parse(self, response):
        pass

    def get_info(self, response):
        '''
            解析员工个人信息
        '''
        # # data = re.sub(r'\u0022', '"', response.body.decode())
        # data = re.findall('share_data = JSON.parse\((".+?")\);</script>.*', response.body.decode())[0]
        #
        # p = re.compile('(null)')
        # p2 = re.compile('(false)')
        # p3 = re.compile('(true)')
        # data = re.sub(p, 'None', data)
        # data = re.sub(p2, 'False', data)
        # data = re.sub(p3, 'True', data)
        #
        # data = eval(data)


        # data = json.loads(data)
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
            item['birth_city'] = NONE_STR(uinfo.get('ht_province', '')) + '-' + NONE_STR(uinfo.get('ht_city', ''))
            if item['birth_city'] == '-':
                item['birth_city'] = ''
            # 星座
            item['xingzuo'] = uinfo.get('xingzuo', '')
            # 生日
            item['birthday'] = NONE_STR(uinfo.get('birthday', ''))

            # 标签
            item['tag'] = ','.join(uinfo['weibo_tags'])
            item['headline'] = uinfo['headline']
            yield item

            # # 工作经历

            # for work_exp in response.xpath('//div[@class="panel-default"][1]//div[@class="media-body"]').extract():
            #     item = WorkItem()
            # item['id'] = id
            # item['company'] = work_exp.xpath('//div[@class="title"]/text()').extract_first()
            # position_time = work_exp('//span[@class="text-muted small"]/text()').extract_first()
            # item['position'] = position_time.split(',')[-1]
            # item['description'] = work_exp.get('description', '')
            # work_time = position_time.split(',')[0]
            # item['start_date'] = work_exp.xpath('-')[0]
            # item['end_date'] = work_exp.xpath('-')[-1]
            # print('= = = '*8)
            for work_exp in uinfo['work_exp']:
                item = WorkItem()
                item['id'] = id
                item['company'] = work_exp['company']
                item['position'] = work_exp['position']
                item['description'] = work_exp.get('description', '')
                item['start_date'] = work_exp['start_date']
                item['end_date'] = WORK_END_DATE(work_exp['end_date'])
                yield item

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
        except Exception as e:
            print('====================================================')
            print(e)
            print('====================================================')
            print(response.body.decode())
            print('====================================================')

    def get_comment(self, response):
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
