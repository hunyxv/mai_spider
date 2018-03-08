# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import base64
import requests
from fake_useragent import UserAgent
from scrapy.http import HtmlResponse
from Maimai.settings import HTTP_PROXY, PORXY_PASSWORD
from Maimai.settings import PROXY_HAS_USER, PROXY_USER
from urllib.parse import unquote
from Maimai.spiders.cookies import get_cookie

user_agent = UserAgent()


# 代理中间件
class IPPOOLS(object):
    def process_request(self, request, spider):
        if PROXY_HAS_USER:
            request.meta['proxy'] = HTTP_PROXY
            proxy_user_pass = '%s:%s' % ((unquote(PROXY_USER)),
                                         unquote(PORXY_PASSWORD))

            encoded_user_pass = base64.b64encode(bytes(
                proxy_user_pass, 'utf-8'))

            request.headers[
                'Proxy-Authorization'] = 'Basic ' + str(
                encoded_user_pass, 'utf-8')


# User—Agent中间件
class UAPOOLS(object):
    def process_request(self, request, spider):
        ua = user_agent.random
        request.headers.setdefault('User-Agent', ua)


# 更新过期cookie中间件
class UPDATECOOKIES(object):
    def process_response(self, request, response, spider):
        if '200' not in str(response):
            COOKIES = get_cookie()
            print(COOKIES)
            cookies = random.choice(COOKIES)
            body = requests.get(
                request.url,
                cookies=cookies,
                headers=request.headers
            ).content
            return HtmlResponse(
                request.url,
                body=body,
                request=request,
            )
        else:
            return response
