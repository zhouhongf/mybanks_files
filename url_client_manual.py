# ManualClient是一个可以独立运行的蜘蛛, 需要Splash, MySQL
# 从url_server获取需要下载的url链接，下载url后，保存至MySQL中
# 并向url_server返回url下载的状态，success or fail
import cchardet
import traceback
import time
import json
import asyncio
import urllib.parse as urlparse
import aiohttp
import farmhash
import lzma
import os
from concurrent.futures import ThreadPoolExecutor as Executor

from myspiders.tools.tools_spider import fetch_bank_cookies
from config.log import Logger
from database.backends import sanic_database


try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class ManualClient:
    config = {
        'host': 'localhost',
        'port': 3306,
        'db': 'mybanks_files',
        'user': 'root',
        'password': '20110919Zyy==20170215Zyy',
    }

    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    LOG_PATH = os.path.join(ROOT_PATH, 'logs')
    os.makedirs(LOG_PATH, exist_ok=True)
    log_file = os.path.join(LOG_PATH, 'ManualClient.log')
    log = Logger(log_file, level='warning').logger

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

    suffix_check = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.html', '.htm', '.shtml', '.shtm', '.zip', '.rar', '.tar', '.bz2', '.7z', '.gz']
    suffix_file = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.zip', '.rar', '.tar', '.bz2', '.7z', '.gz']
    cookie_need_banks = ['浦发银行']
    cookies_available = {}

    manual_type_default_html = ['兴业银行']

    params = {'count': 1000, 'bank': '工商银行'}

    def __init__(self, name):
        self.name = name or 'ManualClient'

        self._workers = 0                 # 当前工作中的线程数
        self.workers_max = 10             # 最大线程数
        self.server_host = 'localhost'
        self.server_port = 9010

        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=self.loop)
        self.sem = asyncio.Semaphore(3)

        self.db = sanic_database.SanicDatabase(
            self.config['host'],
            self.config['db'],
            self.config['user'],
            self.config['password'],
            loop=self.loop
        )
        print('=======================================ManualClient完成初始化=============================================')

    # 向bee-server使用POST发送url的执行结果
    # result参数为字典，包含url， url_real, status, newurls
    async def send_result(self, result):
        url = 'http://%s:%s/fileurls' % (self.server_host, self.server_port)
        try:
            print('发送下载结果到server, 内容: %s' % result)
            async with aiohttp.ClientSession(loop=self.loop) as client:
                async with client.post(url, json=result, timeout=3) as response:
                    return response.status
        except:
            traceback.print_exc()
            pass


    async def save_file(self, url, ukey, content):
        ukeyhash = farmhash.hash64(ukey)
        sql = 'select ukey from crawler_manual where ukeyhash=%s'
        d = await self.db.get(sql, ukeyhash)
        if d:
            if d['ukey'] != ukey:
                self.log.error('farmhash collision: %s <=> %s' % (ukey, d['ukey']))
            return True

        bank_name = ukey.split('=')[0]
        content_type = os.path.splitext(url)[-1]
        print('准备保存%s的内容, 文件类型是：%s' % (ukey, content_type))
        if content_type not in self.suffix_check:
            content_type = '.other'

        if content_type not in self.suffix_file:
            encoding = cchardet.detect(content)['encoding']
            content = content.decode(encoding, errors='ignore')     # content从byte对象变为str对象

        # 有些网页不是以.html结尾的，则在这里重新设置
        if bank_name in self.manual_type_default_html:
            content_type = '.html'

        status = 'undo'
        sql = 'insert into crawler_manual(ukeyhash, ukey, bank_name, content, content_type, status) values(%s, %s, %s, %s, %s, %s)'

        try:
            await self.db.execute(sql, ukeyhash, ukey, bank_name, content, content_type, status)
            good = True
        except Exception as e:
            if e.args[0] == 1062:
                good = True           # Duplicate entry
                pass
            else:
                traceback.print_exc()
                raise e
        return good


    # 根据url下载html页面，返回状态码，html页面
    async def download(self, bank_name, url, timeout=25):
        status_code = 900
        content = ''
        headers = self.headers
        # 如果bank_name在cookie_need_banks[]集合中的，则在headers中添加相应的Cookie
        if bank_name in self.cookie_need_banks:
            headers['Cookie'] = self.cookies_available[bank_name]
            print('Cookie Header已更新：%s' % headers)
        try:
            async with self.sem:
                async with aiohttp.ClientSession(loop=self.loop) as client:
                    async with client.get(url, headers=headers, timeout=timeout) as response:
                        status_code = response.status
                        if status_code == 200:
                            content = await response.read()
        except Exception as e:
            self.log.error('下载失败: {}，exception: {}, {}'.format(url, str(type(e)), str(e)))

        return status_code, content

    # 这是url_client类的 主要 方法, 这个协程会在抓取循环中被不断的创建，达到并发的目的。
    async def consume(self):
        while True:
            item = await self.queue.get()   # 从队列中删除并返回一个元素。如果队列为空，则等待，直到队列中有元素。
            url = item['url']
            ukey = item['ukey']
            bank_name = ukey.split('=')[0]
            status_code, content = await self.download(bank_name, url)
            print('%s请求完成, 状态：%s' % (url, status_code))

            self.queue.task_done()  # 每当消费协程调用 task_done() 表示这个条目item已经被回收，该条目所有工作已经完成，未完成计数就会减少。
            self._workers -= 1
            # print('self._workers减1后，还剩：%s' % self._workers)

            if content:
                if len(content) > 10240:                        # 限制文件大小最小为10kb
                    await self.save_file(url, ukey, content)
                else:
                    status_code = 900
                    await self.queue.put(item)                  # 如果文件大小小于10kb，则说明没有把文件下载下来，将item放回队列中，再次下载

            # 将本次请求的结果通过send_result()方法，发送给url_server
            result = {'ukey': ukey, 'status_code': status_code}
            await self.send_result(result)


    # 根据最大线程数和队列中的线程数的差额，向url_server请求urls
    async def produce(self):
        count = self.workers_max - self.queue.qsize()
        if count <= 0:
            print('【queue队列中的数量，大于设定的workers_max, 因此produce()不需要去服务器请求urls对象，来添加到queue队列中】')
            return None
        url = 'http://%s:%s/fileurls' % (self.server_host, self.server_port)
        try:
            async with aiohttp.ClientSession(loop=self.loop) as client:
                async with client.get(url, params=self.params, timeout=5) as response:
                    if response.status not in [200, 201]:
                        return
                    text = await response.text()
                    jsondata = json.loads(text)
                    print('获取%s条数据' % len(jsondata))

                    bank_names = set()
                    for one in jsondata:
                        ukey = one['ukey']
                        name = ukey.split('=')[0]
                        if name in self.cookie_need_banks:
                            bank_names.add(name)
                        await self.queue.put(one)    # queue的生产者
                    print('【produce请求成功，当前queue队列中的数量为：%s, 当前的_workers数量为：%s】' % (self.queue.qsize(), self._workers))
                    # 如果前面迭代的过程中，发现有需要cookie才能下载的银行存在的，则使用splash去请求cookie
                    if len(bank_names) > 0:
                        for bank_name in bank_names:
                            cookie = await fetch_bank_cookies(bank_name)
                            self.cookies_available[bank_name] = cookie
        except:
            traceback.print_exc()
            return None

    # 爬虫的主流程是在方法loop_crawl()里面实现的。
    async def main(self):
        counter = 0
        last_get = 0
        while True:
            if time.time() - last_get > 60:
                await self.produce()
                last_get = time.time()

            self._workers += 1
            counter += 1

            consumer = asyncio.ensure_future(self.consume())
            await self.queue.join()    # 阻塞至队列中所有的元素都被接收和处理完毕。当未完成计数降到零的时候， join() 阻塞被解除。
            consumer.cancel()

            if self._workers > self.workers_max:
                print('================ 当前的_workers数量%s超过了workers_max的设定%s，休息3秒 ==================' % (self._workers, self.workers_max))
                await asyncio.sleep(3)

    def start(self):
        # executor = Executor()
        # self.loop.set_default_executor(executor)

        self.loop.create_task(self.main())
        try:
            # future = self.loop.run_in_executor(None, blocking阻塞方法)
            self.loop.run_forever()
        except KeyboardInterrupt:
            print('【手动键盘关闭】')
            # tasks = asyncio.Task.all_tasks(loop=self.loop)  # 此方法 已弃用 并将在 Python 3.9 中移除。改用 asyncio.all_tasks() 函数。
            tasks = asyncio.all_tasks()
            group = asyncio.gather(*tasks, return_exceptions=True)
            group.cancel()
            self.loop.run_until_complete(group)
        finally:
            print('【最终loop关闭】')
            # executor.shutdown(wait=True)
            self.loop.close()


def run():
    ManualClient('ManualClient').start()


if __name__ == '__main__':
    run()



