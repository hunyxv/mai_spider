import redis
from pymongo import MongoClient

mongo_cli = MongoClient('localhost', 27017)
db = mongo_cli.maimai_database

redis_pool = redis.ConnectionPool(host='localhost', port=6379)
redis_cli = redis.StrictRedis(connection_pool=redis_pool)


class SQL(object):
    @classmethod
    def set_cookies(cls, cookies):
        redis_cli.set('cookies', cookies)

    @classmethod
    def get_cookies(cls):
        cookies = redis_cli.get('cookies')
        if cookies:
            return cookies.decode()
        return cookies

    @classmethod
    def get_abatch_id(cls):
        all_old = redis_cli.smembers('old_encode_mmids')
        if not all_old:
            return None
        for one in all_old:
            if not redis_cli.exists(one):
                redis_cli.sadd('not_friends', one)

    @classmethod
    def get_target_encode_mmid(cls):
        encode_mmid = redis_cli.spop('not_friends')
        if not encode_mmid:
            if not cls.get_abatch_id():
                return None
            encode_mmid = redis_cli.spop('not_friends')
        encode_mmid = encode_mmid.decode()
        return encode_mmid.split(' :')

    @classmethod
    def sadd_target_encode_mmid(cls, mmid):
        redis_cli.sadd('not_friends', mmid)

    @classmethod
    def sadd_already_friend(cls, encode_mmid, user_id, flag=True):
        if flag:
            redis_cli.set(encode_mmid.split(' :')[1], encode_mmid + '-:' + user_id)
            redis_cli.expire(encode_mmid.split(' :')[1], 60 * 60 * 24 * 7)
        redis_cli.sadd('already_friend', encode_mmid)

    @classmethod
    def already_passed(cls, fid):
        if not redis_cli.keys(fid):
            return False
        redis_cli.delete(fid)
        return True

    @classmethod
    def update_baseitem_email(cls, id, email):
        db_People_info = db.People_Info
        db_People_info.update(
            {'_id': str(id)},
            {
                '$set': {
                    'email': email
                }
            }
        )
        return True

    @classmethod
    def get_friend_url(cls, id):
        db_People_info = db.People_Info
        friend = db_People_info.find_one({'_id': str(id)})
        if friend:
            return friend['url']
        print('> 数据库中没有该好友信息。。')
        return None
