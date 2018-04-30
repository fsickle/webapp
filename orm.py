# -*- coding:utf-8 -*-
import logging; logging.basicConfig(level=logging.INFO)
from aiohttp import web
import asyncio,aiomysql,logging
#一层对 logging.info 的封装，目的事方便输出 sql 语句
def log(sql,args=()):
    logging.info('SQL:%s'%sql)

# 创建连接池，从连接池获取数据库连接
async def create_pool(loop,**kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host','localhost'),
        port=kw.get('port',3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        # 避免从数据库获取到的结果是乱码
        charset=kw.get('charset','utf-8'),
        # 是否自动提交事务，为True，则不用调用 commit 提交事务
        autocommit=kw.get('autocommit',True),
        maxsize=kw.get('maxsize',10),
        minsize=kw.get('minsize',1),
        loop=loop
    )

# Select;;该协程封装的是查询事务,第一个参数为sql语句,第二个为sql语句中占位符的参数列表,第三个参数是要查询数据的数量
async def select(sql,args,size=None):
    log(sql,args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?','%s'),args or ())  # SQL语句的占位符是?，而MySQL的占位符是%s
        if size:
            rs = await cur.fetchmany(size)  # 获取最多指定数量的记录
        else:
            rs = await cur.fetchall()       # 获取所有记录
        await cur.close()
        logging.info('rows returned:%s' % len(rs))
        return rs

# 执行 Insert,Update,Delete;;cursor对象不返回结果集，而是通过rowcount返回结果数
async def execute(sql,args):
    log(sql)
    with (await __pool) as conn:
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?','%s'),args)
            affected = cur.rowcount()
            await cur.close()
        except BaseException as e:
            raise
        return affected

# 简单的 ORM
from orm import Model, StringField, IntegerField
class User(Model):
    __table__='users'    # 类属性，而非实例属性

    id = IntegerField(primary_key=True)
    name = StringField()

# 定义 model
class Model(dict,metaclass=ModelMetacalss):
    def __init__(self,**kw):
        super(Model,self).__init__(**kw)

    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model object has no attribute '%s'" % key)

    def __setattr__(self,key,value):
        self[key] = value

