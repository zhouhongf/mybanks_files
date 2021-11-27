import pymysql
from .db_settings import Settings


class MySQLInit:

    def __init__(self):
        config = Settings.mysqldb_config
        self.database = pymysql.connect(charset="utf8mb4", **config)
        self.init_db()
        # print('name是：%s' % __name__)
        # print('file是：%s' % __file__)

    def init_db(self):
        cursor = self.database.cursor()
        sql_hub = 'CREATE TABLE IF NOT EXISTS crawler_hub (' \
                  'id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT, ' \
                  'url VARCHAR(255) NOT NULL, ' \
                  'bank_name VARCHAR(255) NOT NULL, ' \
                  'html_type VARCHAR(64) NOT NULL, ' \
                  'create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
                  'PRIMARY KEY(id),' \
                  'UNIQUE KEY uidx_url (url)' \
                  ') ENGINE=InnoDB DEFAULT CHARSET=utf8'
        cursor.execute(sql_hub)

        # 用于保存公告，或产品说明书的网页版
        sql_html = 'CREATE TABLE IF NOT EXISTS crawler_html (' \
                   'id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT, ' \
                   'urlhash BIGINT(20) UNSIGNED NOT NULL,' \
                   'url VARCHAR(255) NOT NULL, ' \
                   'bank_name VARCHAR(255) NOT NULL, ' \
                   'html_type VARCHAR(64) NOT NULL, ' \
                   'html_lzma LONGBLOB NOT NULL, ' \
                   'create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
                   'PRIMARY KEY(id),' \
                   'UNIQUE KEY uidx_urlhash (urlhash)' \
                   ') ENGINE=InnoDB DEFAULT CHARSET=utf8'
        cursor.execute(sql_html)

        # 用于解析后的产品说明书
        sql_manual = 'CREATE TABLE IF NOT EXISTS crawler_manual (' \
                     'id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT, ' \
                     'ukeyhash BIGINT(20) UNSIGNED NOT NULL,' \
                     'ukey VARCHAR(255) NOT NULL, ' \
                     'bank_name VARCHAR(255) NOT NULL, ' \
                     'content LONGBLOB NOT NULL, ' \
                     'content_type VARCHAR(20) NOT NULL, ' \
                     'status VARCHAR(20) NOT NULL, ' \
                     'create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, ' \
                     'PRIMARY KEY(id),' \
                     'UNIQUE KEY uidx_ukeyhash (ukeyhash)' \
                     ') ENGINE=InnoDB DEFAULT CHARSET=utf8'
        cursor.execute(sql_manual)
        self.database.close()
        print('=======================================MySQLInit完成初始化================================================')
