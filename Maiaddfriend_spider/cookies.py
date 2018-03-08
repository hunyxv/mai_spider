import time
import os
from requests import Session
from fake_useragent import UserAgent
from Sql import SQL

COOKIE_PATH = os.path.join(os.path.abspath(os.path.dirname(__name__)), 'spiders/cookie.py')

ACCOUNT = [
    {
        'm': '13373189397',
        'p': 'wang5695196',
        'to': None,
        'pa': '+86'
    },
    # {
    #     'm': '**** 手机号 ****',
    #     'p': '**** 密码 ****',
    #     'to': None,
    #     'pa': '+86'
    # }
]

user_agent = UserAgent()
url = 'https://acc.maimai.cn/login'
headers = {
    'origin': 'https://acc.maimai.cn',
    'referer': 'https://acc.maimai.cn/login',
    'user-agent': user_agent.random
}


def get_cookie():
    COOKIES = []
    for acc in ACCOUNT:
        session = Session()
        session.get(url, headers=headers)
        session.post(url, data=acc, headers=headers, verify=False)
        COOKIES.append(dict(session.cookies))

        time.sleep(3)
    SQL.set_cookies(str(COOKIES))
    return COOKIES


if __name__ == '__main__':
    COOKIES = get_cookie()
    for i in COOKIES:
        for k in i:
            print(k + ' : ' + str(i[k]))
