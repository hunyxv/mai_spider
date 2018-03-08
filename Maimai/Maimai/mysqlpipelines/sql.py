# coding=utf-8
import redis
from pymongo import MongoClient

mongo_cli = MongoClient('localhost', 27017)
db = mongo_cli.maimai_database

redis_pool = redis.ConnectionPool(host='localhost', port=6379)
redis_cli = redis.StrictRedis(connection_pool=redis_pool)


class Sql:
    @classmethod
    def insert_baseitem(cls, id, name, sex, birthday, img, company, position, work_city, birth_city, xingzuo, tag,
                        url, headline):
        db_People_info = db.People_Info
        value = {
            '_id': id,
            'name': name,
            'sex': sex,
            'birthday': birthday,
            'img': img,
            'company': company,
            'position': position,
            'work_city': work_city,
            'birth_city': birth_city,
            'xingzuo': xingzuo,
            'tag': tag,
            'url': url,
            'headline': headline,
        }
        db_People_info.insert(value)
        # cur.execute(sql, value)
        # cnx.commit()

    @classmethod
    def insert_workitem(cls, id, work_exp):
        db_People_info = db.People_Info
        db_People_info.update(
            {'_id': str(id)},
            {
                '$set': {
                    'work_exp': work_exp
                }
            }
        )

    @classmethod
    def insert_eduitem(cls, id, education):
        db_People_info = db.People_Info
        db_People_info.update(
            {'_id': str(id)},
            {
                '$set': {
                    'education': education
                }
            }
        )

    @classmethod
    def insert_commentitem(cls, id, comments):
        db_People_info = db.People_Info
        db_People_info.update(
            {'_id': str(id)},
            {
                '$set': {
                    'comments': comments
                }
            }
        )

    @classmethod
    def push_new_encode_mmid(cls, new_encode_mmid, userid):
        # 新获得的没有爬取过的，存到待爬取集合
        if not redis_cli.sismember('old_encode_mmids', new_encode_mmid + ' :' + str(userid)):
            redis_cli.sadd('new_encode_mmids', new_encode_mmid + ' :' + str(userid))

    @classmethod
    def get_new_encode_mmid(cls):
        encode_mmid = redis_cli.spop('new_encode_mmids').decode()
        redis_cli.sadd('old_encode_mmids', encode_mmid)
        return encode_mmid

    @classmethod
    def get_cookies(cls):
        cookies = redis_cli.get('cookies')
        if cookies:
            return cookies.decode()
        return cookies

    @classmethod
    def set_cookies(cls, cookies):
        redis_cli.set('cookies', cookies)