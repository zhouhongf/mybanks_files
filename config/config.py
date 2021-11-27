import os
import sys


class Config:

    PROJECT_NAME = 'mybanks_files'
    CLEAN_NAME = 'mybanks_clean'
    # CRAWL_PAGE_COUNT = 5

    # Application config
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)

    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    os.makedirs(DATA_DIR, exist_ok=True)

    TIMEZONE = 'Asia/Shanghai'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'

    HOST_REMOTE = '192.168.1.104'

    DB_TYPE = os.getenv('DB_TYPE', "redis")
    HOST = ['127.0.0.1:8001', '0.0.0.0:8001']
    START_SPIDER = int(os.getenv('START_SPIDER', '1'))                    # 1或0，是否在项目启动时候马上爬取代理网站
    VAL_HOST = str(os.getenv('VAL_HOST', '0'))                            # 0或1，是否验证请求host，默认不验证

    # scheduled task
    SCHEDULED_DICT = {
        'ver_interval': int(os.getenv('VER_INTERVAL', 10)),               # 定时验证代理数据时间
        'time_interval': int(os.getenv('TIME_INTERVAL', 60)),           # 定时爬取代理数据时间
    }

    # URL config
    TEST_URL = {
        'http': 'http://httpbin.org/get?show_env=1',
        'https': 'https://httpbin.org/get?show_env=1',
        'timeout': 5
    }


    # Database config
    # os.getenv(key, default)用来获取本机环境的环境变量
    # 例如：os.getenv('JAVA_HOME')
    # 返回：'C:\\Program Files\\Java\\jdk1.8.0_221'
    MYSQL_DICT = dict(
        ENDPOINT=os.getenv('MYSQL_ENDPOINT', 'localhost'),
        PORT=int(os.getenv('MYSQL_PORT', 3306)),
        DB=os.getenv('MYSQL_DB', 'myworld_auth'),
        USER=os.getenv('MYSQL_USERNAME', 'root'),
        PASSWORD=os.getenv('MYSQL_PASSWORD', '123456'),
    )

    MONGO_DICT = dict(
        ENDPOINT=os.getenv('MONGO_ENDPOINT', 'localhost'),
        PORT=int(os.getenv('MONGO_PORT', 27017)),
        DB=os.getenv('MONGO_DB', PROJECT_NAME),
        USERNAME=os.getenv('MONGO_USERNAME', 'root'),
        PASSWORD=os.getenv('MONGO_PASSWORD', '123456'),
    )

    # Redis数据库分类：
    # 数据库0：备用
    # 数据库1：保存代理IP
    # 数据库2：保存爬取成功或失败的urls
    REDIS_DICT = dict(
        ENDPOINT=os.getenv('REDIS_ENDPOINT', 'localhost'),
        PORT=int(os.getenv('REDIS_PORT', 6379)),
        DB=int(os.getenv('REDIS_DB', 2)),
        PASSWORD=os.getenv('REDIS_PASSWORD', '123456')
    )

    HTML_TYPE = {
        'manual': '产品说明书',
        'notice_plan': '产品发行公告',
        'notice_start': '产品成立公告',
        'notice_end': '产品终止公告',
    }


    WEALTH_BASE = {
        'base_rate_save': 0.015,
        'base_rate_loan': 0.0435,
    }

