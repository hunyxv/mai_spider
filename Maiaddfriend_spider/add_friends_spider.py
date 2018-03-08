import ast
import json
import re
import time
import requests
from fake_useragent import UserAgent
from urllib import parse
from cookies import get_cookie
from Sql import SQL


class AddFriends(object):
    def __init__(self, cookies, count=5):
        # 每天可以添加好友的次数
        self.count = count
        self.cookies = cookies

    # User-Agent
    user_agent = UserAgent()
    # 申请好友api接口
    add_friend_url = ('https://open.taou.com/maimai/contact'
                      '/v4/pre_init_req?u2={target_id}&acc=&'
                      'u={my_id}&channel=www&version=4.0.0&'
                      '_csrf={my_csrf}&access_token={my_access_token}'
                      '&uid={uid}&token={token}&from=task_list')
    result_url = ('https://open.taou.com/maimai/contact/v4/init_req'
                  '?lv=1&u2={target_id}&acc=&attach={message}'
                  '&from=task_list&u={my_id}&channel=www&version=4.0.0'
                  '&_csrf={my_csrf}&access_token={my_access_token}'
                  '&uid={uid}&token={token}'
                  )
    referer_base = ('https://maimai.cn/contact/detail'
                    '/{encode_mmid}?from=webview%23%2Ffeed_list')

    users_info = []

    # 根据提供的Cookie 获取Cookie的信息
    def get_myuser_info(self):
        while(len(self.cookies)):
            cookie = self.cookies.pop(0)
            user_agent = self.user_agent.random
            my_page_url = 'https://maimai.cn/im/'
            headers = {
                'user-agent': user_agent,
                'referer': 'https://maimai.cn/'
            }
            body = requests.get(
                url=my_page_url,
                cookies=cookie,
                headers=headers,
                verify=False
            )

            html = body.text
            try:
                str_data = re.findall('share_data = JSON.parse\((.+?)\);</script>', html)[0]
            except:
                print('> cookies已失效重新获取中。。。')
                get_cookie()
                print('> 获取成功！')
                self.cookies = ast.literal_eval(SQL.get_cookies())
                self.get_myuser_info()
                continue

            str_data = re.sub('true', 'True', str_data)
            str_data = re.sub('false', 'False', str_data)
            str_data = re.sub('null', 'None', str_data)
            data = ast.literal_eval(ast.literal_eval(str_data))

            auth_info = data['auth_info']
            auth_info['company'] = data['data']['myself']['company']
            auth_info['position'] = data['data']['myself']['position']
            auth_info['name'] = data['data']['myself']['realname']
            auth_info['message'] = '我是{}{} {}，能不能加个好友?'.format(
                auth_info['company'],
                auth_info['position'],
                auth_info['name']
            )
            auth_info['user-agent'] = user_agent
            auth_info['cookie'] = cookie
            self.users_info.append(data['auth_info'])

            time.sleep(5)
        return self.users_info

    def url_format(self,enmmid_and_id, user):
        url = self.add_friend_url.format(
            target_id=enmmid_and_id[1], my_id=user['u'],
            my_csrf=parse.quote_plus(user['_csrf']),
            my_access_token=user['access_token'],
            uid=parse.quote_plus(user['uid']),
            token=parse.quote_plus(user['token'])
        )
        result = self.result_url.format(
            target_id=enmmid_and_id[1],
            message=parse.quote_plus(user['message']),
            my_id=user['u'],
            my_csrf=parse.quote_plus(user['_csrf']),
            my_access_token=user['access_token'],
            uid=parse.quote_plus(user['uid']),
            token=parse.quote_plus(user['token'])
        )
        headers = {
            'user-agent': user['user-agent'],
            'referer': self.referer_base.format(encode_mmid=enmmid_and_id[0]),
            'origin': 'https://maimai.cn'
        }
        return url, result, headers


    # 开始添加好友
    def add_friends(self):
        for user in self.users_info:
            for i in range(self.count):
                enmmid_and_id = SQL.get_target_encode_mmid()
                if enmmid_and_id is None:
                    break
                url, result, headers=self.url_format(enmmid_and_id, user)
                # 发送申请好友请求
                requests.get(url, headers=headers)
                # 查看结果
                resp = requests.get(result, headers=headers)
                try:
                    if json.loads(resp.text)['result'] == 'ok':
                        print(str(enmmid_and_id[1]) + '已经发送好友请求。。')
                        SQL.sadd_already_friend(' :'.join(enmmid_and_id), user['u'])
                except:
                    error_msg = json.loads(resp.text)
                    print(error_msg['error_msg'])
                    SQL.sadd_already_friend(' :'.join(enmmid_and_id), user['u'], flag=False)
                    if error_msg['error_code'] == 30000:
                        SQL.sadd_target_encode_mmid(enmmid_and_id.join(' :'))
                        break

                time.sleep(10)

    def run(self):
        print('> 开始发送好友请求。。。')
        self.get_myuser_info()
        self.add_friends()


if __name__ == '__main__':
    cookies = SQL.get_cookies()
    if not cookies:
        add_friend = AddFriends([{}])
    add_friend = AddFriends(ast.literal_eval(cookies))

    add_friend.run()
