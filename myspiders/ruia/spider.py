# 仿照Scrapy的Spider类，允许Spider子类增加form_data实例属性，类型为list，用来发起POST请求
# 不管是默认运行，还是自定义运行，只要存在form_data，则默认request的method是POST
# 只要form_data存在，没有start_urls，或者start_urls长度大于1，都会抛出错误
# 不存在form_data，也不存在start_urls，则执行自定义请求start_manual()方法来生成request实例
import asyncio
import collections
import typing
import weakref
import time
from datetime import datetime
from functools import reduce
from inspect import isawaitable
from signal import SIGINT, SIGTERM
from types import AsyncGeneratorType
from aiohttp import ClientSession

from .exceptions import (
    InvalidCallbackResult,
    NotImplementedParseError,
    NothingMatchedError,
)
from .item import Item
from .middleware import Middleware
from .request import Request
from .response import Response
from config.log import Logger
from database.backends import MongoDatabase, MySQLDatabase

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class SpiderHook:
    """
    SpiderHook is used for extend spider
    """

    callback_result_map: dict = None
    logger = Logger(level='warning').logger

    async def _run_spider_hook(self, hook_func):
        """
        Run hook before/after spider start crawling
        :param hook_func: aws function
        :return:
        """
        if callable(hook_func):
            try:
                aws_hook_func = hook_func(weakref.proxy(self))
                if isawaitable(aws_hook_func):
                    await aws_hook_func
            except Exception as e:
                self.logger.error(f"<Hook {hook_func.__name__}: {e}")

    async def process_failed_response(self, request, response):
        """
        Corresponding processing for the failed response
        :param request: Request
        :param response: Response
        :return:
        """
        pass

    async def process_succeed_response(self, request, response):
        """
        Corresponding processing for the succeed response
        :param request: Request
        :param response: Response
        :return:
        """
        pass

    async def process_item(self, item):
        """
        Corresponding processing for the Item type
        :param item: Item
        :return:
        """
        pass

    async def process_callback_result(self, callback_result):
        """
        Corresponding processing for the invalid callback result
        :param callback_result: Custom instance
        :return:
        """
        print('来到Spider中process_callback_result()方法, callback_result参数是:%s' % callback_result)
        callback_result_name = type(callback_result).__name__
        print('Spider中process_callback_result()方法中callback_result_name为：%s' % callback_result_name)
        process_func_name = self.callback_result_map.get(callback_result_name, "")
        print('Spider中process_callback_result()方法中process_func_name为：%s' % process_func_name)
        process_func = getattr(self, process_func_name, None)
        print('Spider中process_callback_result()方法中process_func 为：%s' % process_func)
        if process_func is not None:
            await process_func(callback_result)
        else:
            raise InvalidCallbackResult(f"process_callback_result()方法中<Parse invalid callback result type: {callback_result_name}>")


class Spider(SpiderHook):
    """
    Spider is used for control requests better
    Spider可以说是爬虫程序的入口，它将Item、Middleware、Request、等模块组合在一起
    你只需要关注以下两个函数：
    Spider.start：爬虫的启动函数
    parse：爬虫的第一层解析函数，继承Spider的子类必须实现这个函数
    """

    name = None
    request_config = None
    # request_session = None

    # Default values passing to each request object. Not implemented yet.
    headers: dict = None
    metadata: dict = None
    kwargs: dict = None

    # Some fields for statistics
    failed_counts: int = 0
    success_counts: int = 0

    # Concurrency control
    worker_numbers: int = 2
    concurrency: int = 3

    # A queue to save coroutines
    worker_tasks: list = []

    def __init__(
            self,
            name=None,
            start_urls: list = None,
            middleware: typing.Union[typing.Iterable, Middleware] = None,
            loop=None,
            is_async_start: bool = False,
            cancel_tasks: bool = True,
            **kwargs,
    ):
        """
        Init spider object.
        :param middleware: a list of or a single Middleware
        :param loop: asyncio event llo
        :param is_async_start: start spider by using async
        :param kwargs
        """
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)

        # 如果类属性中没有start_urls，那么从实例属性中获取，如果实例属性中也没有start_urls，那么为空集合
        if not hasattr(self, 'start_urls'):
            self.start_urls = start_urls or []
            print('Spider子类%s中start_urls为：%s' % (self.name, self.start_urls))
        else:
            self.start_urls = getattr(self, 'start_urls')
            if not isinstance(self.start_urls, collections.Iterable):
                raise ValueError("start_urls must be collections.Iterable")

        # 如果类属性中有form_data，且为list, 那么该spider运行的请求将都是POST请求
        self.form_data = getattr(self, 'form_data', None)
        if self.form_data:                                       # 如果Spider子类中定义了form_data，
            if not isinstance(self.form_data, collections.Iterable):
                raise ValueError("form_data must be collections.Iterable")     # 但form_data不是list的格式，则抛出错误
            if len(self.start_urls) != 1:                        # 在form_data存在的前提下，没有start_urls，或者start_urls长度大于1，都会抛出错误
                raise ValueError("form_data exists, so method is POST, therefore start_urls must have only one child")     # 但start_urls集合长度不等于1，则抛出错误

        self.loop = loop
        asyncio.set_event_loop(self.loop)
        # async queue as a producer 在实例化Spider时，新建一个Queue队列
        self.request_queue = asyncio.Queue()
        # semaphore, used for concurrency control 定义协程的最大线程数
        self.sem = asyncio.Semaphore(self.concurrency)

        # Init object-level properties  SpiderHook的类属性
        self.callback_result_map = self.callback_result_map or {}

        self.headers = self.headers or {}
        self.metadata = self.metadata or {}
        self.kwargs = self.kwargs or {}
        self.request_config = self.request_config or {}
        self.request_session = ClientSession()
        self.cancel_tasks = cancel_tasks
        self.is_async_start = is_async_start

        # customize middleware
        if isinstance(middleware, list):
            # middleware集合相加
            self.middleware = reduce(lambda x, y: x + y, middleware)
        else:
            self.middleware = middleware or Middleware()

        if not hasattr(self, 'bank_name'):
            raise ValueError("%s must have a bank_name, to setup database" % type(self).__name__)
        else:
            self.bank_name = getattr(self, 'bank_name')

        # Mongo数据库
        self.mongo = MongoDatabase()
        mongo_db = self.mongo.db()
        collection_ukey = mongo_db['BANK_UKEY']
        self.mongo.do_insert_one(collection_ukey, {'_id': self.bank_name}, {'_id': self.bank_name, 'ukey': 'bank_name=code'})
        self.collection_list = mongo_db[self.bank_name]      # 保存理财列表信息
        self.collection_file = mongo_db['MANUAL_URL']        # 保存理财说明书链接

        # MySQL数据库
        self.mysql_db = MySQLDatabase()


    # 重要！处理异步回调函数的方法，在start_worker()方法中，启动该方法
    # 从返回结果callback_results中迭代每一个返回结果callback_result, 根据其不同的类别，套用不同的执行方法
    async def _process_async_callback(self, callback_results: AsyncGeneratorType, response: Response = None):
        try:
            async for callback_result in callback_results:
                if isinstance(callback_result, AsyncGeneratorType):
                    await self._process_async_callback(callback_result)
                elif isinstance(callback_result, Request):
                    self.request_queue.put_nowait(
                        self.handle_request(request=callback_result)
                    )
                elif isinstance(callback_result, typing.Coroutine):
                    self.request_queue.put_nowait(
                        self.handle_callback(aws_callback=callback_result, response=response)
                    )
                elif isinstance(callback_result, Item):
                    await self.process_item(callback_result)
                else:
                    await self.process_callback_result(callback_result=callback_result)
        except NothingMatchedError as e:
            error_info = f"<Field: {str(e).lower()}" + f", error url: {response.url}>"
            self.logger.error(error_info)
        except Exception as e:
            self.logger.error(e)

    async def _process_response(self, request: Request, response: Response):
        if response:
            if response.ok:
                # Process succeed response
                self.success_counts += 1
                await self.process_succeed_response(request, response)
            else:
                # Process failed response
                self.failed_counts += 1
                await self.process_failed_response(request, response)

    async def _run_request_middleware(self, request: Request):
        if self.middleware.request_middleware:
            for middleware in self.middleware.request_middleware:
                if callable(middleware):
                    try:
                        aws_middleware_func = middleware(self, request)
                        if isawaitable(aws_middleware_func):
                            await aws_middleware_func
                        else:
                            self.logger.error(f"<Middleware {middleware.__name__}: must be a coroutine function")
                    except Exception as e:
                        self.logger.error(f"<Middleware {middleware.__name__}: {e}")

    async def _run_response_middleware(self, request: Request, response: Response):
        if self.middleware.response_middleware:
            for middleware in self.middleware.response_middleware:
                if callable(middleware):
                    try:
                        aws_middleware_func = middleware(self, request, response)
                        if isawaitable(aws_middleware_func):
                            await aws_middleware_func
                        else:
                            self.logger.error(f"<Middleware {middleware.__name__}: must be a coroutine function")
                    except Exception as e:
                        self.logger.error(f"<Middleware {middleware.__name__}: {e}")

    # 2、从start()方法或async_start()传递进来，添加signal和hook后，执行start_master()
    async def _start(self, after_start=None, before_stop=None):
        self.logger.info("Spider started!")
        start_time = datetime.now()

        # Add signal 添加控制信号，不过只有在linux系统上才行
        for signal in (SIGINT, SIGTERM):
            try:
                self.loop.add_signal_handler(
                    signal, lambda: asyncio.ensure_future(self.stop(signal))
                )
            except NotImplementedError:
                self.logger.warning(f"{self.name} tried to use loop.add_signal_handler but it is not implemented on this platform.")

        # Run hook before spider start crawling 添加SpiderHook，蜘蛛钩子，after_start
        await self._run_spider_hook(after_start)

        # Actually run crawling  真正开始爬取了。。。
        try:
            await self.start_master()
        finally:
            # Run hook after spider finished crawling 添加SpiderHook，蜘蛛钩子, before_stop
            await self._run_spider_hook(before_stop)
            # 关闭aiohttp的ClientSession()
            await self.request_session.close()

            # Display logs about this crawl task 本次蜘蛛爬取工作的日志处理，成功次数，失败次数，用时多久
            end_time = datetime.now()
            self.logger.info(f"Total requests: {self.failed_counts + self.success_counts}")
            if self.failed_counts:
                self.logger.info(f"Failed requests: {self.failed_counts}")
            self.logger.info(f"Time usage: {end_time - start_time}")
            self.logger.info(f"Spider finished at time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 1、spider完成实例化后，通过spider_console文件中的spider_module.async_start()来启动
    @classmethod
    async def async_start(
            cls,
            start_urls: list = None,
            middleware: typing.Union[typing.Iterable, Middleware] = None,
            loop=None,
            after_start=None,
            before_stop=None,
            cancel_tasks: bool = True,
            **kwargs,
    ):
        """
        Start an async spider
        :param start_urls: 改造原来的方法，新增的参数，用来传递start_urls集合，实例化Spider
        :param middleware: customize middleware or a list of middleware  中间件类，可以是一个中间件Middleware()实例，也可以是一组Middleware()实例组成的列表
        :param loop:
        :param after_start: hook
        :param before_stop: hook
        :param cancel_tasks: cancel async tasks
        :param kwargs: Additional keyword args to initialize spider
        :return: An instance of :cls:`Spider`
        """
        # 因为是异步启动async_start, 所以事件循环应该已经定义好了，所以使用get_event_loop()来获取loop实例，
        # 并且不需要执行run_until_complete()和loop.close()方法了
        loop = loop or asyncio.get_event_loop()
        # async_start()方法中，生成一个Spider实例为spider_ins，比start()方法多2个参数is_async_start, cancel_tasks
        # 实例化Spider类时定义cancel_tasks为True, 则，取消前面的tasks, 执行当前异步启动的task
        spider_ins = cls(start_urls=start_urls, middleware=middleware, loop=loop, is_async_start=True, cancel_tasks=cancel_tasks, **kwargs)
        # spider_ins实例执行_start()方法
        await spider_ins._start(after_start=after_start, before_stop=before_stop)
        print('async_start()方法执行完spider_ins._start()')
        return spider_ins

    # 1、spider完成实例化后，通过spider_console文件中的spider_module.start()来启动
    # 定义事件循环loop, 实例化Spider类
    # 通过含有loop属性的实例化的Spider, 来启动_start()任务
    # 添加事件循环loop的shutdown_asyncgens()任务
    @classmethod
    def start(
            cls,
            start_urls: list = None,
            middleware: typing.Union[typing.Iterable, Middleware] = None,
            loop=None,
            after_start=None,
            before_stop=None,
            close_event_loop=True,
            **kwargs,
    ):
        """
        Start a spider
        :param start_urls: 改造原来的方法，新增的参数，用来传递start_urls集合，实例化Spider
        :param after_start: hook  爬虫启动后的钩子函数
        :param before_stop: hook  爬虫停止前的钩子函数
        :param middleware: customize middleware or a list of middleware  中间件类，可以是一个中间件Middleware()实例，也可以是一组Middleware()实例组成的列表
        :param loop: event loop   事件循环
        :param close_event_loop: bool
        :param kwargs: Additional keyword args to initialize spider
        :return: An instance of :cls:`Spider`
        """
        loop = loop or asyncio.new_event_loop()
        # start()方法中，生成一个Spider实例为spider_ins
        spider_ins = cls(start_urls=start_urls, middleware=middleware, loop=loop, **kwargs)

        # Actually start crawling，         spider_ins实例执行_start()方法
        spider_ins.loop.run_until_complete(spider_ins._start(after_start=after_start, before_stop=before_stop))
        spider_ins.loop.run_until_complete(spider_ins.loop.shutdown_asyncgens())
        if close_event_loop:
            spider_ins.loop.close()

        return spider_ins

    # 处理callback回调，类型为typing.Coroutine, 包含response
    # 主要是处理Item实例中的回调结果
    async def handle_callback(self, aws_callback: typing.Coroutine, response):
        """Process coroutine callback function"""
        callback_result = None
        try:
            callback_result = await aws_callback
        except NothingMatchedError as e:
            self.logger.error(f"<Item: {str(e).lower()}>")
        except Exception as e:
            self.logger.error(f"<Callback[{aws_callback.__name__}]: {e}")

        return callback_result, response

    # 6 、主要是用于添加middleware
    async def handle_request(self, request: Request) -> typing.Tuple[AsyncGeneratorType, Response]:
        """
        Wrap request with middleware.
        :param request:
        :return:
        """
        callback_result, response = None, None

        # 运行request的带callback的fetch方法，传入参数是semaphore, 用以控制并发量
        try:
            # 执行request的middleware
            await self._run_request_middleware(request)
            callback_result, response = await request.fetch_callback(self.sem)
            # 执行response的middleware
            await self._run_response_middleware(request, response)
            # 处理response，记录request请求成功或失败的次数
            await self._process_response(request=request, response=response)
        except NotImplementedParseError as e:
            self.logger.error(e)
        except NothingMatchedError as e:
            error_info = f"<Field: {str(e).lower()}" + f", error url: {request.url}>"
            self.logger.error(error_info)
        except Exception as e:
            self.logger.error(f"<Callback[{request.callback.__name__}]: {e}")

        return callback_result, response

    # 6、处理多个handle_request方法
    # 用来解决asyncio出现too many file descriptors in select()问题的web请求
    async def multiple_request(self, urls, is_gather=False, **kwargs):
        """For crawling multiple urls"""
        if is_gather:
            resp_results = await asyncio.gather(
                *[self.handle_request(self.request(url=url, **kwargs)) for url in urls],
                return_exceptions=True,
            )
            for index, task_result in enumerate(resp_results):
                if not isinstance(task_result, RuntimeError) and task_result:
                    _, response = task_result
                    response.index = index
                    yield response
        else:
            for index, url in enumerate(urls):
                _, response = await self.handle_request(self.request(url=url, **kwargs))
                response.index = index
                yield response

    async def parse(self, response):
        """
        Used for subclasses, directly parse the responses corresponding with start_urls
        :param response: Response
        :return:
        """
        raise NotImplementedParseError("<!!! parse function is expected !!!>")

    # 4、遍历spider中start_urls集合或form_data集合，生成request实例, 返回request的集合
    async def process_start_urls(self):
        """
        Process the start URLs
        :return: AN async iterator
        """
        # 如果存在form_data, 则默认url为start_url集合中的第一条记录，然后遍历form_data集合，迭代出request
        if self.form_data:
            url = self.start_urls[0]
            for data in self.form_data:
                yield self.request(url=url, form_data=data, callback=self.parse, metadata=self.metadata)
        else:
            # 如果不存在form_data, 则遍历start_urls集合，迭代出request
            for url in self.start_urls:
                yield self.request(url=url, callback=self.parse, metadata=self.metadata)

    # 如果spider子类中没有start_ulrs，则执行start_manual()方法来，手工yield出来request实例
    # spider子类需重写此方法, 并且返回的方法，最好也是parse()
    async def start_manual(self):
        yield self.request()

    # 5、request()方法，用以生成requests实例
    # 改造request()方法，增加参数url的默认值为http://httpbin.org/get，用以应对start_manual()方法中，没有url参数的情况
    def request(
            self,
            url: str = 'http://httpbin.org/get',
            method: str = "GET",
            *,
            callback=None,
            encoding: typing.Optional[str] = None,
            headers: dict = None,
            metadata: dict = None,
            request_config: dict = None,
            request_session=None,
            form_data: dict = None,
            **kwargs,
    ):
        """Init a Request class for crawling html"""
        headers = headers or {}
        metadata = metadata or {}
        request_config = request_config or {}
        request_session = request_session or self.request_session
        # 如果Spider子类中定义了form_data成员属性，那么form_data一定会传递到Request实例中
        form_data = form_data

        headers.update(self.headers.copy())
        request_config.update(self.request_config.copy())
        kwargs.update(self.kwargs.copy())
        # 如果存在form_data，则method为POST，否则为默认的GET
        method = 'POST' if form_data else method

        return Request(
            url=url,
            method=method,
            callback=callback,
            encoding=encoding,
            headers=headers,
            metadata=metadata,
            request_config=request_config,
            request_session=request_session,
            form_data=form_data,
            **kwargs,
        )

    # 3（1）根据spider子类中的参数内容，实例化request或request集合，放入异步队列queue中
    # 此处，可以考虑拿出来，做定制化请求
    async def start_master(self):
        """Actually start crawling."""
        # 如果有start_urls，则执行默认的process_start_urls()方法，来产生request实例
        if len(self.start_urls) > 0:
            async for request_ins in self.process_start_urls():
                self.request_queue.put_nowait(self.handle_request(request_ins))
        else:
            # 如果没有start_urls，则执行start_manual()方法，来产生request实例
            async for request_ins in self.start_manual():
                self.request_queue.put_nowait(self.handle_request(request_ins))

        await self.start_fetch()

    # 3（2）
    async def start_fetch(self):
        workers = [asyncio.ensure_future(self.start_worker()) for i in range(self.worker_numbers)]
        for worker in workers:
            self.logger.info(f"Worker started: {id(worker)}")
        await self.request_queue.join()      # 阻塞至队列中所有的元素都被接收和处理完毕。当未完成计数降到零的时候， join() 阻塞被解除。

        # 运行到此处，代表request_queue队列中的任务都执行完成了，不再受到requests_queue.join()方法的阻塞了。
        # 然后执行的是关闭任务，和关闭loop的操作了。
        if not self.is_async_start:          # 如果不是is_async_start，即不是异步启动的，则等待执行stop()方法
            await self.stop(SIGINT)
        else:
            if self.cancel_tasks:            # 如果是异步启动的，在async_start()方法中，实例化Spider类时定义cancel_tasks为True, 则，取消前面的tasks, 执行当前异步启动的task
                await self._cancel_tasks()

    # 3（3）为队列queue的消费者，从队列中取出request, 放入tasks中
    async def start_worker(self):
        while True:
            request_item = await self.request_queue.get()
            self.worker_tasks.append(request_item)
            if self.request_queue.empty():
                results = await asyncio.gather(*self.worker_tasks, return_exceptions=True)
                for task_result in results:
                    # 如果task_result不是RuntimeError的实例，并且task_result为True
                    if not isinstance(task_result, RuntimeError) and task_result:
                        callback_results, response = task_result
                        # 如果callback_results是属于AsyncGeneratorType的实例的
                        if isinstance(callback_results, AsyncGeneratorType):
                            # 等待执行 异步返回操作_process_async_callback()
                            await self._process_async_callback(callback_results, response)
                self.worker_tasks = []
            self.request_queue.task_done()    # 每当消费协程调用 task_done() 表示这个条目item已经被回收，该条目所有工作已经完成，未完成计数就会减少。

    # 该方法只能在linux系统中操作，停止所有的任务，停止事件循环
    async def stop(self, _signal):
        """
        Finish all running tasks, cancel remaining tasks, then stop loop.
        :param _signal:
        :return:
        """
        self.logger.info(f"Stopping spider: {self.name}")
        await self._cancel_tasks()
        self.loop.stop()

    # 将不是当前的task取消后，放入tasks集合
    async def _cancel_tasks(self):
        tasks = []
        for task in asyncio.Task.all_tasks():
            if task is not asyncio.tasks.Task.current_task():
                tasks.append(task)
                task.cancel()
        # 如果 return_exceptions为True，异常会和成功的结果一样处理，并聚合至结果列表。
        # 任一 Task 或 Future 对象 被取消，它将被当作引发了 CancelledError 一样处理 -- 在此情况下 gather() 调用 不会 被取消。
        # 如果 gather() 被取消，所有被提交 (尚未完成) 的可等待对象也会 被取消。
        await asyncio.gather(*tasks, return_exceptions=True)
