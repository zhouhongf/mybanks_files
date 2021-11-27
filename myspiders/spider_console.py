import os
import sys
import time
from config import CONFIG
from config import Logger
from importlib import import_module

#sys.path.append('../')


def file_name(file_dir=os.path.join(CONFIG.BASE_DIR, 'myspiders/spider_pdf')):

    print('spider_console中显示的file_dir是：%s' % file_dir)
    all_files = []
    for file in os.listdir(file_dir):
        if file.endswith('_spider.py') and file != 'demo_spider.py':
            all_files.append(file.replace('.py', ''))
    return all_files


def spider_console():
    start = time.time()
    all_files = file_name()

    for spider in all_files:
        spider_module = import_module("myspiders.spider_pdf.{}".format(spider))
        spider_module.start()

    #time.sleep(10)
    #mongodb_module = import_module("database.backends.mongo_database")
    #mongodb_module.backup_database()

    logger = Logger(level='warning').logger
    logger.info("Time costs: {0}".format(time.time() - start))


if __name__ == '__main__':
    spider_console()
