# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
import base64
from Maimai.proxy import PROXIES
from fake_useragent import UserAgent

user_agent = UserAgent()


class IPPOOLS(object):
    def process_request(self, request, spider):
        proxy = random.choice(PROXIES)

        # 对账户密码进行base64编码转换
        base64_userpasswd = base64.b64encode(proxy['user_passwd'])

        # 对应到代理服务器的信令格式里
        request.headers['Proxy-Authorization'] = 'Basic ' + base64_userpasswd
        request.meta['proxy'] = 'http://' + proxy['ip_port']


class UAPOOLS(object):
    def process_request(self, request, spider):
        ua = user_agent.random
        request.headers.setdefault('User-Agent', ua)
