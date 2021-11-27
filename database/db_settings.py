from config import CONFIG


class Settings:
    """Global Settings"""
    mysqldb_config = {
        'host': CONFIG.MYSQL_DICT['ENDPOINT'],
        'port': CONFIG.MYSQL_DICT['PORT'],
        'db': CONFIG.MYSQL_DICT['DB'],
        'user': CONFIG.MYSQL_DICT['USER'],
        'password': CONFIG.MYSQL_DICT['PASSWORD'],
    }

    redisdb_config = {
        'host': CONFIG.REDIS_DICT['ENDPOINT'],
        'port': CONFIG.REDIS_DICT['PORT'],
        'db': CONFIG.REDIS_DICT['DB'],
        'password': CONFIG.REDIS_DICT['PASSWORD'],
    }

    mongodb_config = {
        'host': CONFIG.MONGO_DICT['ENDPOINT'],
        'port': CONFIG.MONGO_DICT['PORT'],
        'db': CONFIG.MONGO_DICT['DB'],
        'username': CONFIG.MONGO_DICT['USERNAME'],
        'password': CONFIG.MONGO_DICT['PASSWORD'],
    }

    host_remote = CONFIG.HOST_REMOTE

    database_spider = 'mybanks_files'
    database_cleaner = 'mybanks_cleaner'
    database_myworld = 'myworld'
