# coding=utf-8

import pymysql
import redis

MYSQL_HOSTS = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'toor'
MYSQL_PORT = 3306
MYSQL_DB = 'maimai'

cnx = pymysql.connect(user=MYSQL_USER, passwd=MYSQL_PASSWORD, host=MYSQL_HOSTS, db=MYSQL_DB, port=MYSQL_PORT,
                      charset='utf8')
cur = cnx.cursor()

redis_pool = redis.ConnectionPool(host='localhost', port=6379)
redis_cli = redis.StrictRedis(connection_pool=redis_pool)

class Sql:
    @classmethod
    def insert_baseitem(cls, id, name, sex, birthday, img, company, position, work_city, birth_city, xingzuo, tag,
                        url, headline):
        sql = (
            'INSERT INTO baseitem '
            '(ID, NAME, SEX, BIRTHDAY, IMG, COMPANY, POSITION, '
            'WORK_CITY, BIRTH_CITY, XINGZUO, TAG, URL, HEADLINE) '
            'VALUES '
            '(%(id)s, %(name)s, %(sex)s, %(birthday)s, %(img)s, '
            '%(company)s, %(position)s, %(work_city)s, %(birth_city)s, '
            '%(xingzuo)s, %(tag)s, %(url)s, %(headline)s)'
        )
        value = {
            'id': id,
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
        cur.execute(sql, value)
        cnx.commit()

    @classmethod
    def insert_workitem(cls, id, company, position, description, start_date, end_date):
        sql = (
            'INSERT INTO workitem '
            '(ID, COMPANY, POSITION, DESCRIPTION, START_DATE, END_DATE) '
            'VALUES '
            '(%(id)s, %(company)s, %(position)s, %(description)s, '
            '%(start_date)s, %(end_date)s)'
        )
        value = {
            'id': id,
            'company': company,
            'position': position,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
        }
        cur.execute(sql, value)
        cnx.commit()

    @classmethod
    def insert_eduitem(cls, id, school, degree, department, start_date, end_date):
        sql = (
            'INSERT INTO eduitem '
            '(ID, SCHOOL, DEGREE, DEPARTMENT, START_DATE, END_DATE) '
            'VALUES '
            '(%(id)s, %(school)s, %(degree)s, %(department)s, %(start_date)s, %(end_date)s)'
        )
        value = {
            'id': id,
            'school': school,
            'degree': degree,
            'department': department,
            'start_date': start_date,
            'end_date': end_date,
        }
        cur.execute(sql, value)
        cnx.commit()

    @classmethod
    def insert_commentitem(cls, id, friend_id, friend_name, friend_company, friend_position, level, comment):
        sql = (
            'INSERT INTO commentitem '
            '(ID, FRIEND_ID, FRIEND_NAME, FRIEND_COMPANY, FRIEND_POSITION, LEVEL, COMMENT) '
            'VALUES '
            '(%(id)s, %(friend_id)s, %(friend_name)s, %(friend_company)s, '
            '%(friend_position)s, %(level)s, %(comment)s)'
        )
        value = {
            'id': id,
            'friend_id': friend_id,
            'friend_name': friend_name,
            'friend_company': friend_company,
            'friend_position': friend_position,
            'level': level,
            'comment': comment,
        }
        cur.execute(sql, value)
        cnx.commit()

    @classmethod
    def insert_simpleitem(cls, id, cid, name, loc, company, position, encode_mmid, url):
        sql = (
            'insert into simpleitem '
            '(id, cid, name, loc, company, position, encode_mmid, url) '
            'values '
            '(%(id)s, %(cid)s, %(name)s, %(loc)s, %(company)s, '
            '%(position)s, %(encode_mmid)s, %(url)s)'
        )
        value = {
            'id': id,
            'cid': cid,
            'name': name,
            'loc': loc,
            'company': company,
            'position': position,
            'encode_mmid': encode_mmid,
            'url': url,
        }
        cur.execute(sql, value)
        cnx.commit()

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
