from pymongo import MongoClient, collection
from config.decorators import singleton
from ..db_settings import Settings
import bson.binary
from gridfs import *
import time
from utils.time_util import datetime_to_timestamp
from .elastic_database import update_myworld_wealth_from_mongo


MONGODB = Settings.mongodb_config

@singleton
class MongoDatabase:

    # ===================================初始化数据库并建立连接=========================================
    # 数据量一多，频繁的增删查改，将极大的占用硬盘空间，
    # 如果是大数据储存，建议使用MySQL

    def client(self):
        mongo = MongoClient(
            host=MONGODB['host'] if MONGODB['host'] else 'localhost',
            port=MONGODB['port'] if MONGODB['port'] else 27017,
            username=MONGODB['username'] if MONGODB['username'] else '',
            password=MONGODB['password'],
        )
        return mongo

    def db(self):
        return self.client()[MONGODB['db']]

    @staticmethod
    def upsert(collec: collection, condition: dict, data: dict):
        result = collec.find_one(condition)
        if result:
            collec.update_one(condition, {'$set': data})
            print('MONGO数据库《%s》中upsert更新: %s' % (collec.name, condition))
            return None
        else:
            collec.insert_one(data)
            print('MONGO数据库《%s》中upsert新增: %s' % (collec.name, condition))
            return condition

    @staticmethod
    def do_insert_one(collec: collection, condition: dict, data: dict):
        result = collec.find_one(condition)
        if result:
            print('MONGO数据库《%s》中do_insert_one已存在: %s' % (collec.name, condition))
            return None
        else:
            collec.insert_one(data)
            print('MONGO数据库《%s》中do_insert_one新增: %s' % (collec.name, condition))
            return condition


def backup_database():
    time_start = time.perf_counter()
    print('===================================运行MongoDB备份: %s=========================================' % time_start)
    mongo = MongoDatabase()
    mongo_db = mongo.db()
    collection_client_ukey = mongo_db['BANK_UKEY']
    collection_client_url = mongo_db['MANUAL_URL']

    mongo_server = MongoClient(host=Settings.host_remote, port=27017, username=MONGODB['username'], password=MONGODB['password'])
    try:
        mongo_db_server = mongo_server[MONGODB['db']]
        collection_server_ukey = mongo_db_server['BANK_UKEY']
        collection_server_url = mongo_db_server['MANUAL_URL']

        client_ukeys = collection_client_ukey.find()
        for ukey in client_ukeys:
            condition = {'_id': ukey['_id']}
            result = collection_server_ukey.find_one(condition)
            if not result:
                collection_server_ukey.insert_one(ukey)

        client_urls = collection_client_url.find({'crawl_status': 'undo'})
        if client_urls.count() > 0:
            for data in client_urls:
                condition = {'_id': data['_id']}
                result = collection_server_url.find_one(condition)
                if not result:
                    done = collection_server_url.insert_one(data)
                    if done:
                        data['crawl_status'] = 'uploaded'
                        collection_client_url.update_one(condition, {'$set': data})
        else:
            print('MANUAL_URL数据库中没有还没有上传到server的记录')
    except:
        print('===================================未能连接远程SERVER=======================================')

    time_end = time.perf_counter()
    print('===================================完成MongoDB备份: %s, 用时: %s=========================================' % (time_end, (time_end - time_start)))


# 将WEALTH_CLEAN中的理财数据导入到wealth数据库中
def update_myworld_wealth():
    time_start = time.perf_counter()
    print('===================================运行MongoDB更新wealth: %s=========================================' % time_start)
    mongo = MongoDatabase().client()
    db_origin = mongo[Settings.database_spider]
    db_target = mongo[Settings.database_myworld]
    collection_origin = db_origin['WEALTH_CLEAN']
    collection_target = db_target['wealth']

    data_origin = collection_origin.find()
    for data in data_origin:
        condition = {'_id': data['_id']}
        result = collection_target.find_one(condition)
        if not result:
            fee_types_new = ''
            fee_types = data['fee_types']
            if fee_types:
                for k, v in fee_types.items():
                    fee_types_new += (str(k) + ':' + str(v) + ',')
                fee_types_new = fee_types_new[:-1]

            sale_ways_new = ''
            sale_ways = data['sale_ways']
            if sale_ways:
                for one in sale_ways:
                    sale_ways_new += (one + ',')
                sale_ways_new = sale_ways_new[:-1]

            data_new = {}
            for k, v in data.items():
                if k == 'fee_types':
                    data_new[k] = fee_types_new
                elif k == 'sale_ways':
                    data_new[k] = sale_ways_new
                else:
                    data_new[k] = v

            collection_target.insert_one(data_new)

    time_end = time.perf_counter()
    print('===================================完成MongoDB更新wealth: %s, 用时: %s=========================================' % (time_end, (time_end - time_start)))


# 从MySQL中将PDF文件数据导入到MongoDB中
def update_myworld_pdfs(dataList: list):
    time_start = time.perf_counter()
    print('===================================运行MongoDB更新wealth: %s=========================================' % time_start)
    mongo = MongoDatabase().client()
    db_target = mongo[Settings.database_myworld]
    collection_target = db_target['manual']

    for one in dataList:
        condition = {'_id': str(one['ukeyhash'])}
        result = collection_target.find_one(condition)
        if not result:
            create_time = datetime_to_timestamp(one['create_time'])
            data = {
                '_id': str(one['ukeyhash']),
                'ukey': one['ukey'],
                'bank_name': one['bank_name'],
                'content_type': one['content_type'],
                'status': one['status'],
                'create_time': str(create_time),
                'content': one['content']
            }
            collection_target.insert_one(data)

    time_end = time.perf_counter()
    print('===================================完成MongoDB更新wealth: %s, 用时: %s=========================================' % (time_end, (time_end - time_start)))


# 将MongoDB中wealth的部分数据导出到ElasticSearch中，供搜索使用
def dump_data_elastic():
    mongo = MongoDatabase().client()
    db_origin = mongo[Settings.database_myworld]
    collection_origin = db_origin['wealth']

    dataList = collection_origin.find()
    update_myworld_wealth_from_mongo(dataList)


