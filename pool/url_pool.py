import pickle
from redis import StrictRedis
import time
import urllib.parse as urlparse


class UrlDB:
    # 数据库2：保存爬取成功或失败的urls
    # 使用Redis散列【h开头】
    # key的格式：银行名称:HTTP/HTTPS:HOST
    # value的格式：key为path，value为1/0
    status_failure = 0
    status_success = 1

    def __init__(self, db_name):
        self.bank_name = db_name
        self.db = StrictRedis(host='localhost', password='Zhouhf873@', port=6379, db=2, decode_responses=True)
        print('=======================================UrlDB完成初始化================================================')

    def set_success(self, url):
        up = urlparse.urlparse(url)
        scheme = up.scheme
        host = up.netloc
        path = up.path
        key = self.bank_name + ':' + scheme + ':' + host
        try:
            self.db.hset(key, path, self.status_success)
            s = True
        except:
            s = False
        return s

    def set_failure(self, url):
        up = urlparse.urlparse(url)
        scheme = up.scheme
        host = up.netloc
        path = up.path
        key = self.bank_name + ':' + scheme + ':' + host
        try:
            self.db.hset(key, path, self.status_failure)
            s = True
        except:
            s = False
        return s

    def has(self, url):
        up = urlparse.urlparse(url)
        scheme = up.scheme
        host = up.netloc
        path = up.path
        key = self.bank_name + ':' + scheme + ':' + host
        try:
            value = self.db.hget(key, path)
            return value
        except:
            pass
        return False


class UrlPool:
    '''URL Pool for crawler to manage URLs'''

    def __init__(self, pool_name):
        self.name = pool_name or 'url_pool'
        self.db = UrlDB(pool_name)                          # 一个UrlDB的示例，用来永久存储url的永久状态

        self.waiting = {}                                   # {host: set([urls])} 按host分组，记录等待下载的URL；key是url的host，value是一个用来存储这个host的所有url的集合(set)。
        self.pending = {}                                   # {url: pended_time} 记录已被取出（self.pop()）但还未被更新状态（正在下载）的URL；key是url，value是它被pop的时间戳。
        self.failure = {}                                   # {url: times} 记录失败的URL的次数
        self.failure_threshold = 3
        self.pending_threshold = 10                         # pending的最大时间，过期要重新下载
        self.waiting_count = 0                              # self.waiting 字典里面的url的个数
        self.max_hosts = ['', 0]                            # [host, url_count] 目前pool中url最多的host及其url数量
        self.hub_pool = {}                                  # {url: last_query_time}, 用来存储hub页面的字典，key是hub url，value是上次刷新该hub页面的时间.
        self.hub_refresh_span = 0
        self.load_cache()                                   # 创建pool的时候，尝试去加载上次退出时缓存的URL pool
        print('=======================================UrlPool完成初始化================================================')

    def __del__(self):
        self.dump_cache()                                   # 在网址池销毁前（比如爬虫意外退出），把内存中的URL pool缓存到硬盘。
        print('=======================================UrlPool已销毁================================================')

    # 1. load_cache() 和 dump_cache() 对网址池进行缓存
    # (1) load_cache()创建pool的时候，尝试去加载上次退出时缓存的URL pool
    def load_cache(self,):
        path = self.name + '.pkl'
        try:
            with open(path, 'rb') as f:
                self.waiting = pickle.load(f)
            cc = [len(v) for k, v in self.waiting.items()]
            print('saved pool loaded! urls:', sum(cc))
        except:
            pass

    # 1. load_cache() 和 dump_cache() 对网址池进行缓存
    # dump_cache() 在网址池销毁前（比如爬虫意外退出），把内存中的URL pool缓存到硬盘。
    def dump_cache(self):
        path = self.name + '.pkl'
        try:
            with open(path, 'wb') as f:
                pickle.dump(self.waiting, f)
            print('self.waiting saved!')
        except:
            pass

    #  2. set_hubs() 方法设置hub URL
    # hub网页就是像百度新闻那样的页面，整个页面都是新闻的标题和链接，是我们真正需要的新闻的聚合页面，并且这样的页面会不断更新，
    # 把最新的新闻聚合到这样的页面，我们称它们为hub页面，其URL就是hub url。
    # 在新闻爬虫中添加大量的这样的url，有助于爬虫及时发现并抓取最新的新闻。
    def set_hubs(self, hub_urls, hub_refresh_span):
        # （1）将hub url列表传给网址池，在爬虫从池中取URL时，根据时间间隔（self.hub_refresh_span）来取hub url。
        self.hub_refresh_span = hub_refresh_span
        # （2）self.hub_pool字典{url: last_query_time, },  存放hub_url为key, 上次查询时间last_query_time为value的字典
        self.hub_pool = {}
        for hub_url in hub_urls:
            url = hub_url['url']
            self.hub_pool[url] = 0


    # 3. add(), addmany(), push_to_pool() 对网址池进行入池操作
    # 把url放入网址池时，先检查内存中的self.pending是否存在该url，即是否正在下载该url。
    def add(self, url, always=False):
        # (1)如果always为True，则不作判断，直接入池push_to_pool
        if always:
            return self.push_to_pool(url)

        # 获取该url的pended_time, 如果self.pending字典中存在该url, 则可取出该url对应的时间，
        # 否则，即没有该url, 则pended_time当然为0
        pended_time = self.pending.get(url, 0)

        # (2)如果该url被pended的时间（time.time() - pended_time）小于pending_threshold
        # 则return，暂不入池。即正在下载就不入池了。
        if time.time() - pended_time < self.pending_threshold:
            print('【being downloading:%s】' % url)
            return

        # (3)检查该url是否已经在leveldb中存在，存在就表明之前已经成功下载或彻底失败，不再下载了也不入池。
        if self.db.has(url):
            return

        # （4）如果pended_time成立, 则从self.pending字典{url: pended_time}中移除该url
        if pended_time:
            self.pending.pop(url)

        # （5）通过push_to_pool() 把url放入self.pool下载池中准备下载。
        return self.push_to_pool(url)

    def addmany(self, urls, always=False):
        if isinstance(urls, str):
            print('urls is a str !!!!', urls)
            self.add(urls, always)
        else:
            for url in urls:
                self.add(url, always)

    # 3 .存放的规则是，按照url的host进行分类，相同host的url放到一起，在取出时每个host取一个url，
    # 尽量保证每次取出的一批url都是指向不同的服务器的，这样做的目的也是为了尽量减少对抓取目标服务器的请求压力。
    def push_to_pool(self, url):
        # 从url中取出host
        host = urlparse.urlparse(url).netloc

        # 检查host是否符合标准，否则返回False
        if not host or '.' not in host:
            print('try to push_to_pool with bad url:', url, ', len of ur:', len(url))
            return False

        # 如果host是在self.waiting字典{host: set([urls]), }中的
        if host in self.waiting:
            # 如果该url是在host为key的set([urls])集合中的，返回True
            if url in self.waiting[host]:
                return True

            # 如果该url不在host为key的set([urls])集合中的，则在self.waiting字典{host: set([urls]), }中新增一条记录
            self.waiting[host].add(url)

            # 重新检查 目前self.waiting等待下载的pool中，url最多的host及其url数量
            # 如果该host为key，该host下的url的数量超过self.max_hosts中第2个元素，即len(urls)数量的，
            # 则将self.max_hosts更新为：第一个0位置的为该host，第二个1位置的为len(self.waiting[host])
            if len(self.waiting[host]) > self.max_hosts[1]:
                self.max_hosts[1] = len(self.waiting[host])
                self.max_hosts[0] = host
        else:
            # 如果host不在self.waiting字典{host: set([urls]), }中的，
            # 则在self.waiting字典中添加, key为该host，value为set([url])即该  url集合的字典
            # set([url]) 等同于{url}
            self.waiting[host] = {url}

        # self.waiting_count加1
        self.waiting_count += 1
        return True

    #  4. pop() 对网址池进行出池操作
    # 爬虫通过该方法，从网址池中获取一批url去下载。
    def pop(self, count, hub_percent=50):
        print('\n\tmax of host:', self.max_hosts)
        # 取出的url有两种类型：hub=1, 普通=0
        url_attr_url = 0
        url_attr_hub = 1

        # （1）首先取出hub，保证获取hub里面的最新url.
        hubs = {}
        # 按照hub_percent的占比，取出整数个hub-url
        hub_count = count * hub_percent // 100
        # 遍历hub_pool
        for hub in self.hub_pool:
            # 检查每个hub_url距上次被pop的时间间隔， self.hub_pool[hub]即为last_query_time
            # 是否超过hub页面刷新间隔(self.hub_refresh_span)来决定hub-url是否应该被pop。
            span = time.time() - self.hub_pool[hub]
            if span < self.hub_refresh_span:
                continue
            # 将该hub_url在hubs={}字典中，key为hub_url, value设置为1， 1即代表url_attr_hub
            hubs[hub] = url_attr_hub
            # 更新hub_pool中 {url: last_query_time}, 该hub_url的查询时间
            self.hub_pool[hub] = time.time()
            # 如果取出的hubs的数量，超过了设定的hub_count数值，则跳出循环
            if len(hubs) >= hub_count:
                break

        # （2）再取出普通url
        # count中剩下的数量，从普通url池中取出
        left_count = count - len(hubs)
        urls = {}
        # 按host（self.pool的key）遍历self.waiting池
        for host in self.waiting:
            # waiting字典为{host: set([urls])}， waiting[host]即可取出set()值，如果为空，则continue继续循环
            if not self.waiting[host]:
                continue
            # 根据key为host，从self.waiting中pop()出一条url, 同时在self.waiting中删除该条
            url = self.waiting[host].pop()
            # 将该url标注为0， 即url_attr_url，表示为普通url
            urls[url] = url_attr_url

            # self.pending字典{url: pended_time, } 记录已被取出（self.pop()）但还未被更新状态（正在下载）的URL
            self.pending[url] = time.time()
            # 如果排名第一的host是该url对应的host, 则max_hosts中排名第二的减去1
            if self.max_hosts[0] == host:
                self.max_hosts[1] -= 1

            # 如果取出的普通url的数量，超过了剩余的额度left_count, 则停止循环
            if len(urls) >= left_count:
                break

        # self.waiting 字典里面的url的个数 减去总共取出的urls数量
        self.waiting_count -= len(urls)
        # 打印 总共取出的数量，其中hubs多少条，普通urls多少条，elf.waiting字典里面还剩多少条
        print('To pop:%s, hubs: %s, urls: %s, hosts:%s' % (count, len(hubs), len(urls), len(self.waiting)))

        # 将hubs字典，添加合并到urls字典中
        urls.update(hubs)
        # 返回总的取出的urls条数
        return urls

    # 5. set_status() 方法设置网址池中url的状态
    # 其参数status_code 是http响应的状态码。爬虫在下载完URL后进行url状态设置。
    def set_status(self, url, status_code):
        # 首先，把该url从self.pending中删除，已经下载完毕，不再是pending状态；
        if url in self.pending:
            self.pending.pop(url)

        # 接着，根据status_code来设置url状态，200和404的直接设置为永久状态；
        if status_code == 200:
            self.db.set_success(url)
            return
        if status_code == 404:
            self.db.set_failure(url)
            return

        # 其它status就记录失败次数，并再次入池进行后续下载尝试。
        if url in self.failure:
            # 在self.failure字典{url: times} 中记录失败的URL的次数，加1
            self.failure[url] += 1
            # 如果失败次数大于设定的阈值，则将此url从self.failure字典移除，并在db中设置为永久状态
            if self.failure[url] > self.failure_threshold:
                self.db.set_failure(url)
                self.failure.pop(url)
            else:
                # 如果失败次数未超过设定的阈值，则重新加回 网址池
                self.add(url)
        else:
            # 如果在self.failure字典没有找到，则新建failure[url] = 1, 表示失败第一次
            self.failure[url] = 1
            # 再重新加回网址池
            self.add(url)

    def size(self,):
        return self.waiting_count

    def empty(self,):
        return self.waiting_count == 0


def test():
    pool = UrlPool('crawl_urlpool')
    urls = [
        'http://1.a.cn/xyz',
        'http://2.a.cn/xyz',
        'http://3.a.cn/xyz',
        'http://1.b.cn/xyz-1',
        'http://1.b.cn/xyz-2',
        'http://1.b.cn/xyz-3',
        'http://1.b.cn/xyz-4',
    ]
    pool.addmany(urls)
    del pool

    pool = UrlPool('crawl_urlpool')
    urls = pool.pop(5)
    urls = list(urls.keys())
    print('pop:', urls)
    print('pending:', pool.pending)

    pool.set_status(urls[0], 200)
    print('pending:', pool.pending)
    pool.set_status(urls[1], 404)
    print('pending:', pool.pending)


if __name__ == '__main__':
    test()
