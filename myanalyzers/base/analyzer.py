import asyncio
from datetime import datetime
from signal import SIGINT, SIGTERM
from config.log import Logger
from database.backends import MySQLDatabase
from database.backends import MongoDatabase
from utils.time_util import get_last_sunday
from constants.bank_dict import BankDict
from myanalyzers.base.wealth_analysis import WealthAnalysis


try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Analyzer:
    logger = Logger(level='warning').logger

    failed_counts: int = 0
    success_counts: int = 0

    # concurrency: int = 3
    worker_numbers: int = 3   # 如果速度太快了，则试试改为数字1
    worker_tasks: list = []   # A queue to save coroutines

    def __init__(self, loop=None, is_async_start: bool = False, cancel_tasks: bool = True, **kwargs):
        # 如果没有定义analyzer_name, 则使用start_init()方法启动
        self.analyzer_name = getattr(self, 'analyzer_name', None)
        # 初始化时需指定WealthAnalysis父类的子类的类型
        self.wealth_analysis = getattr(self, 'wealth_analysis', None)
        if not self.wealth_analysis:
            raise ValueError("%s must have a wealth_analysis element" % type(self).__name__)
        if not issubclass(self.wealth_analysis, WealthAnalysis):
            raise ValueError("wealth_analysis must be the subclass of WealthAnalysis")

        self.loop = loop
        asyncio.set_event_loop(self.loop)
        self.queue = asyncio.Queue()
        # self.sem = asyncio.Semaphore(self.concurrency)
        self.cancel_tasks = cancel_tasks
        self.is_async_start = is_async_start

        self.mongo = MongoDatabase()
        self.db = self.mongo.db()
        self.collection_cleans = self.db['WEALTH_CLEAN']

        self.list_bank_type = BankDict.list_bank_type

    @classmethod
    async def async_start(cls, loop=None, cancel_tasks: bool = True, **kwargs):
        loop = loop or asyncio.get_event_loop()
        tasks_ins = cls(loop=loop, is_async_start=True, cancel_tasks=cancel_tasks, **kwargs)
        await tasks_ins._start()
        return tasks_ins

    @classmethod
    def start(cls, loop=None, close_event_loop=True, **kwargs):
        loop = loop or asyncio.new_event_loop()
        tasks_ins = cls(loop=loop, **kwargs)
        tasks_ins.loop.run_until_complete(tasks_ins._start())
        tasks_ins.loop.run_until_complete(tasks_ins.loop.shutdown_asyncgens())
        if close_event_loop:                # 运行结束之后，需要关闭loop
            tasks_ins.loop.close()
        return tasks_ins

    # 添加stop信号
    async def _start(self):
        self.logger.info("Analyzer started!")
        start_time = datetime.now()

        for signal in (SIGINT, SIGTERM):
            try:
                self.loop.add_signal_handler(signal, lambda: asyncio.ensure_future(self.stop(signal)))
            except NotImplementedError:
                self.logger.warning("Analyzer.py tried loop.add_signal_handler but not implemented on this platform.")

        await self.start_master()

        end_time = datetime.now()
        self.logger.info(f"Total counts: {self.failed_counts + self.success_counts}")
        if self.failed_counts:
            self.logger.info(f"Failed counts: {self.failed_counts}")
        self.logger.info(f"Time usage: {end_time - start_time}")

    # 真正启动，消息队列的生产者
    async def start_master(self):
        async for task_in in self.init_data():
            self.queue.put_nowait(self.handle_task(task_in))

        # 使用worker_numbers来控制并发数量, ensure_future()创建任务
        workers = [asyncio.ensure_future(self.start_worker()) for i in range(self.worker_numbers)]
        for worker in workers:
            self.logger.info(f"Worker started: {id(worker)}")
        await self.queue.join()              # 阻塞至队列中所有的元素都被接收和处理完毕。当未完成计数降到零的时候， join() 阻塞被解除。

        # 执行关闭任务和关闭loop的操作。
        if not self.is_async_start:          # 在async_start()方法中, 如果实例化cleaner时is_async_start=True，则等待执行stop()方法
            await self.stop(SIGINT)
        else:
            if self.cancel_tasks:            # 在async_start()方法中, 如果实例化cleaner时cancel_tasks=True, 则取消前面的tasks, 执行当前异步启动的task
                await self._cancel_tasks()

    # 队列queue的消费者，从队列中取出handle_task(task_in)方法并执行， 有返回值
    async def start_worker(self):
        while True:
            request_item = await self.queue.get()
            self.worker_tasks.append(request_item)
            if self.queue.empty():
                results = await asyncio.gather(*self.worker_tasks, return_exceptions=True)
                for task_result in results:
                    if not isinstance(task_result, RuntimeError) and task_result:
                        result_back = task_result
                self.worker_tasks = []          # 执行完本轮任务后，self.worker_tasks重新还原为空集合
            self.queue.task_done()              # 每当消费协程调用 task_done() 表示这个条目item已经被回收，该条目所有工作已经完成，未完成计数就会减少。

    async def stop(self, _signal):
        self.logger.info("Stopping: Analyzer")
        await self._cancel_tasks()
        self.loop.stop()

    # 将不是当前的task取消后，放入tasks集合
    async def _cancel_tasks(self):
        tasks = []
        for task in asyncio.Task.all_tasks():
            if task is not asyncio.tasks.Task.current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    # (1) 从Mongo数据库中，获取各家银行，本周新增的理财数据wealth
    # (2) 将wealth转换成wealthAnalysis子类
    # (3) 设置取一周的数据，范围为上周日到现在(本周六)
    async def init_data(self):
        last_sunday = get_last_sunday()         # 日期格式为2019-11-06 20:47:35
        for bank_name, bank_type in self.list_bank_type.items():
            select = {'bank_name': bank_name, 'create_time': {'$gt': last_sunday}}
            counts = self.collection_cleans.count_documents(select)
            if counts:
                dict_data = {'bank_name': bank_name, 'bank_type': bank_type, 'last_sunday': last_sunday}
                yield dict_data

    # 此处用来扩展添加，处理各家银行各自内容的分析方法
    async def handle_task(self, data_in):
        result_back = ''
        return result_back



