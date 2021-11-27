import os
import sys
import time
from config import CONFIG
import schedule
from myspiders.spider_console import spider_console
from mycleaners.cleaner_console import cleaner_console
from myanalyzers.analyzer_console import analyzer_console
from database.database_console import database_console

# 将scheduled_task.py文件所在的目录的绝对路径添加到环境变量中去
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def refresh_task(time_interval):
    schedule.every(time_interval).minutes.do(spider_console)
    time.sleep(2)
    # schedule.every(time_interval).minutes.do(cleaner_console)
    # time.sleep(2)
    # schedule.every(time_interval).minutes.do(analyzer_console)

    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == '__main__':
    spider_console()
    time.sleep(2)
    # cleaner_console()
    # time.sleep(2)
    # analyzer_console()
    # time.sleep(2)
    # database_console()

    time_interval = CONFIG.SCHEDULED_DICT['time_interval']
    refresh_task(time_interval=time_interval)
