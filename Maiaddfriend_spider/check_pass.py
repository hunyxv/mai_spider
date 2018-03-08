import ast
import json
import time
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from add_friends_spider import AddFriends
from cookies import get_cookie
from urllib import parse
from Sql import SQL


referer = 'https://maimai.cn/im/'

friends_list_url = (
    'https://open.taou.com/maimai/contact/v4/pbd1?'
    'version=4.0.0&ver_code=web_1&channel=www&push_permit=1'
    '&u={id}&_csrf={csrf}&'
    'access_token={access_token}&'
    'uid="{uid}"&token="{token}"&'
    'json=1&paginate=0'
)
person_referer = ('https://maimai.cn/contact/detail/{}?'
                  'from=webview#/company/contacts')

def get_user_info():
    cookies = SQL.get_cookies()
    if cookies:
        user_info = AddFriends(ast.literal_eval(cookies)).get_myuser_info()
    else:
        cookies = get_cookie()
        user_info = AddFriends(cookies).get_myuser_info()
    return user_info

def check_pass():
    print('> 开始查看之前加的好友是否通过。。。')
    user_info = get_user_info()
    for user in user_info:
        my_friends_list_url = friends_list_url.format(
            id=user['u'], csrf=parse.quote_plus(user['_csrf']),
            access_token=parse.quote_plus(user['access_token']),
            uid=parse.quote_plus(user['uid']),
            token=parse.quote_plus(user['token'])
        )
        headers = {
            'user-agent': user['user-agent'],
            'referer': referer
        }
        # 我的好友列表
        body = requests.get(my_friends_list_url, headers=headers)
        friends_list = json.loads(body.text)
        time.sleep(3)
        friends_list = friends_list['data']

        # 遍历每个好友 获得邮箱地址
        for friend in friends_list:
            if SQL.already_passed(friend['id']):
                url = SQL.get_friend_url(friend['id'])
                if url:
                    friend_info = json.loads(
                        requests.get(
                            url, cookies=user['cookie'],
                            headers={
                                'user-agent': user['user-agent'],
                                'referer': url.split('?')[0] + '?from=webview%23%2Ffeed_list'
                            }
                        ).text
                    )
                    email = friend_info['data']['uinfo']['email']
                    if email and SQL.update_baseitem_email(friend['id'], email):
                        print('【%s】已通过好友邀请并 获得邮箱地址 >: %s' % (friend['name'], email))
                    time.sleep(3)


if __name__ == '__main__':
    sched = BlockingScheduler()
    check_pass()
    sched.add_job(check_pass, 'interval', days=1)
    count = 5
    add_friend = AddFriends(ast.literal_eval(SQL.get_cookies()),count)
    add_friend.run()
    sched.add_job(add_friend.run, 'interval', days=1)

    sched.start()
