# 爬虫Client，负责URL的下载、网页的解析以及存储等各种。
# Client通过接口向Server请求需要被下载的URL，下载完成后向Server报告URL是否下载成功，
# 同时把从网页中提取到的URLs提交给Server，Server把它们放入URLPool。
import cchardet
import traceback
import time
import json
import asyncio
import urllib.parse as urlparse
import aiohttp
from database.backends import sanic_database
import farmhash
import lzma
import requests
from config.log import Logger
from database.db_settings import Settings
from myspiders.filters.url_filter import extract_links_re

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class CrawlerClient:
    config = Settings.mysqldb_config

    def __init__(self, name):
        # 通过self._workers和self._workers_max来控制并发量。
        # 不能一直并发，给本地CPU、网络带宽带来压力，同样也会给目标服务器带来压力。
        self._workers = 0                 # 当前工作中的线程数
        self.workers_max = 10             # 最大线程数
        self.server_host = 'localhost'
        self.server_port = 8080
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0'}

        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.db = sanic_database.SanicDatabase(
            self.config['host'],
            self.config['db'],
            self.config['user'],
            self.config['password'],
            loop=self.loop
        )
        self.logger = Logger(name)

        self.hub_hosts = None
        self.requests_hubs()
        print('=======================================CrawlerClient完成初始化=============================================')
        print('name是：%s' % __name__)
        print('file是：%s' % __file__)


    # 根据url下载html页面，返回状态码，html页面，和新的url
    async def download(self, url, timeout=25):
        status_code = 900
        html = ''
        url_now = url
        try:
            async with self.session.get(url_now, headers=self.headers, timeout=timeout) as response:
                status_code = response.status
                html = await response.read()
                encoding = cchardet.detect(html)['encoding']
                html = html.decode(encoding, errors='ignore')
                url_now = str(response.url)
        except Exception as e:
            # traceback.print_exc()
            print('=== exception: ', e, type(e), str(e))
            msg = 'Failed download: {} | exception: {}, {}'.format(url, str(type(e)), str(e))
            print(msg)
        return status_code, html, url_now

    # 根据最大线程数和队列中的线程数的差额，向bee-server请求urls
    async def get_urls(self,):
        count = self.workers_max - self.queue.qsize()
        # 如果队列中的数量已达到最大线程数，则返回，不执行
        if count <= 0:
            print('no need to get urls this time')
            return None

        # 根据设定的url格式，从bee-server中请求urls
        url = 'http://%s:%s/task?count=%s' % (
            self.server_host,
            self.server_port,
            count
        )

        try:
            async with self.session.get(url, timeout=3) as response:
                if response.status not in [200, 201]:
                    return
                # bee-server返回的是json数据，bee-client以str格式接收，
                jsn = await response.text()
                # 然后再转换为json格式的list, list的数量即为传给server的count参数的数值
                urls = json.loads(jsn)

                msg = ('get_urls()  to get [%s] but got[%s], @%s') % (
                    count, len(urls),
                    time.strftime('%Y-%m-%d %H:%M:%S'))
                print(msg)

                # 将从bee-server获取到的urls集合加入到asyncio的queue队列中去
                # 通过items()方法，kv为字典键值对形式，放入queue
                for kv in urls.items():
                    await self.queue.put(kv)    # queue的生产者
                print('queue size:', self.queue.qsize(), ', _workers:', self._workers)
        except:
            traceback.print_exc()
            return

    # 向bee-server使用POST发送url的执行结果
    # result参数为字典，包含url， url_real, status, newurls
    async def send_result(self, result):
        url = 'http://%s:%s/task' % (
            self.server_host,
            self.server_port
        )
        try:
            async with self.session.post(url, json=result, timeout=3) as response:
                return response.status
        except:
            traceback.print_exc()
            pass

    # 保存url和html到数据库
    # save_html()根据自己需要可以把下载的网页保存到数据库
    async def save_html(self, url, html):
        print('saved:', url, len(html))
        urlhash = farmhash.hash64(url)
        sql = 'select url from crawler_html where urlhash=%s'
        d = await self.db.get(sql, urlhash)
        if d:
            if d['url'] != url:
                msg = 'farmhash collision: %s <=> %s' % (url, d['url'])
                self.logger.error(msg)
            return True
        if isinstance(html, str):
            html = html.encode('utf8')
        html_lzma = lzma.compress(html)
        sql = 'insert into crawler_html(urlhash, url, html_lzma) values(%s, %s, %s)'
        good = False
        try:
            await self.db.execute(sql, urlhash, url, html_lzma)
            good = True
        except Exception as e:
            if e.args[0] == 1062:
                # Duplicate entry
                good = True
                pass
            else:
                traceback.print_exc()
                raise e
        return good

    # filter_good()清洗提取到的URLs，把不需要下载的URLs扔掉。
    def filter_good(self, urls):
        goodlinks = []
        for url in urls:
            host = urlparse.urlparse(url).netloc
            if host in self.hub_hosts:
                goodlinks.append(url)
        return goodlinks

    # 这是url_client类的 主要 方法
    # process()这个方法的流程是下载网页并存储、提取新的url
    # process()是个协程定义，它的工作就是下载、提取、保存、提交，
    # 这个协程会在抓取循环中被不断的创建，达到并发的目的。
    async def process(self, url, ishub):
        # ！！先通过aiohttp下载网页
        status, html, url_now = await self.download(url)

        self._workers -= 1
        print('downloaded:', url, ', html:', len(html))

        # 从html页面中，按照正则规则提取出新的urls,并过滤出符合要求的urls
        if html:
            newurls = extract_links_re(url, html)
            newurls = self.filter_good(newurls)
            await self.save_html(url, html)
        else:
            newurls = []

        # 将本次请求的结果通过send_result()方法，发送给bee-server
        result = {
            'url': url,
            'url_real': url_now,
            'status': status,
            'newurls': newurls,
        }
        await self.send_result(result)

    # 爬虫的主流程是在方法loop_crawl()里面实现的。
    async def loop_crawl(self,):
        print('loop_crawl() start')
        # asyncio.ensure_future(self.loop_get_urls())
        counter = 0
        last_get = 0

        # 主体是一个while循环，每次通过get_urls()方法
        # 从bee-server服务器上的urlpool里获取定量的爬虫作为下载任务, （生产者）放入asyncio的queue中
        while 1:
            # 如果当前时间跟上次抓取的时间相差5以上，则可以从pool中get_urls(), 并将last_get设置为当前时间
            if time.time() - last_get > 5:
                await self.get_urls()
                last_get = time.time()

            # 从队列中获取item, 为key, value形式,
            # 包含url，url_level可能表示优先级，用以区分hub-url和普通url
            item = await self.queue.get()                # queue的消费者
            url, url_level = item

            # 线程数加1，counter加1
            self._workers += 1
            counter += 1

            # 执行异步process()方法, url_level表示是否为hub-url
            asyncio.ensure_future(self.process(url, url_level))

            # 如果当前工作中的线程数，大于设定的最大线程数，则协程休息3秒
            if self._workers > self.workers_max:
                print('====== got workers_max, sleep 3 sec to next worker =====')
                await asyncio.sleep(3)

    def start(self):
        try:
            self.loop.run_until_complete(self.loop_crawl())
        except KeyboardInterrupt:
            print('stopped by yourself!')
            pass

    def requests_hubs(self):
        url = 'http://%s:%s/hubs' % (
            self.server_host,
            self.server_port
        )
        try:
            print('请求hubs，链接：%s' % url)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.json()
                msg = content['msg']
                if msg == 'ok':
                    self.hub_hosts = content['data']
                else:
                    print('未能获取到hub_hosts')
            else:
                print('请求失败：%s' % response.status_code)
        except:
            traceback.print_exc()
            pass


def run():
    client = CrawlerClient('test')     # 通过构造方法初始化一个
    client.start()                     # 启动


if __name__ == '__main__':
    run()

