# 从MySQL数据库中取出manual
# 根据manual的文件类型，应用不同的方法，读取manual的content
import asyncio
from datetime import datetime
from signal import SIGINT, SIGTERM
from config.log import Logger
from collections import namedtuple
from database.backends import MySQLDatabase
from database.backends import MongoDatabase
import os
from config import CONFIG
from utils.file_util import divide_pdf_tables_text, divide_word_tables_text, divide_html_tables_text
import cchardet


try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Cleaner:
    logger = Logger(level='warning').logger
    Manual = namedtuple("Manual", "ukey content content_type")

    file_path = os.path.join(CONFIG.BASE_DIR, 'data\\manual')
    os.makedirs(file_path, exist_ok=True)

    suffix_file = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.zip', '.rar', '.tar', '.bz2', '.7z', '.gz']

    metadata: dict = None
    kwargs: dict = None

    failed_counts: int = 0
    success_counts: int = 0

    # concurrency: int = 3
    worker_numbers: int = 3   # 如果速度太快了，则试试改为数字1
    worker_tasks: list = []   # A queue to save coroutines

    def __init__(self, name=None, loop=None, is_async_start: bool = False, cancel_tasks: bool = True, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)

        self.bank_level = getattr(self, 'bank_level', None)
        if not self.bank_level:
            raise ValueError("%s must set bank_level at class level" % type(self).__name__)

        self.bank_name = getattr(self, 'bank_name', None)               # 如果没有定义bank_name, 则使用start_init()方法启动
        self.other_file_type = getattr(self, 'other_file_type', None)   # 子类在实例化时，在类元素中定义保存在数据库中的.other类型manual,应该保存为何种类型的文件

        self.loop = loop
        asyncio.set_event_loop(self.loop)
        self.queue = asyncio.Queue()
        # self.sem = asyncio.Semaphore(self.concurrency)

        self.metadata = self.metadata or {}
        self.kwargs = self.kwargs or {}

        self.cancel_tasks = cancel_tasks
        self.is_async_start = is_async_start

        # 数据流向是从MySQL到Mongo
        self.db = MySQLDatabase()
        self.mongo = MongoDatabase()
        mongo_db = self.mongo.db()
        self.collection_cleans = mongo_db['WEALTH_CLEAN']

    @classmethod
    async def async_start(cls, loop=None, cancel_tasks: bool = True, **kwargs):
        # 因为是异步启动async_start, 所以事件循环应该已经定义好了，所以使用get_event_loop()来获取loop实例，并且不需要执行run_until_complete()和loop.close()方法了
        loop = loop or asyncio.get_event_loop()
        cleaner_ins = cls(loop=loop, is_async_start=True, cancel_tasks=cancel_tasks, **kwargs)
        await cleaner_ins._start()
        return cleaner_ins

    @classmethod
    def start(cls, loop=None, close_event_loop=True, **kwargs):
        loop = loop or asyncio.new_event_loop()
        cleaner_ins = cls(loop=loop, **kwargs)
        cleaner_ins.loop.run_until_complete(cleaner_ins._start())
        cleaner_ins.loop.run_until_complete(cleaner_ins.loop.shutdown_asyncgens())
        if close_event_loop:                # 运行结束之后，需要关闭loop
            cleaner_ins.loop.close()
        return cleaner_ins

    async def _start(self):
        self.logger.info("Cleaner started!")
        start_time = datetime.now()

        for signal in (SIGINT, SIGTERM):
            try:
                self.loop.add_signal_handler(signal, lambda: asyncio.ensure_future(self.stop(signal)))
            except NotImplementedError:
                self.logger.warning(f"{self.name} tried loop.add_signal_handler but not implemented on this platform.")

        await self.start_master()

        end_time = datetime.now()
        self.logger.info(f"Total manuals: {self.failed_counts + self.success_counts}")
        if self.failed_counts:
            self.logger.info(f"Failed manuals: {self.failed_counts}")
        self.logger.info(f"Time usage: {end_time - start_time}")

    async def start_master(self):
        if self.bank_name:
            for manual_in in self.process_bank_name():
                self.queue.put_nowait(self.handle_manual(manual_in))
        else:
            for manual_in in self.start_init():
                self.queue.put_nowait(self.handle_manual(manual_in))

        # 使用workers用来控制并发数量, ensure_future()创建任务，任务为：使用start_worker方法从队列queue中取出divide_pdf_tables_text(manual_in)方法并执行
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

    # 根据bank_name，从MySQL数据库中，select出来还没有被处理的manual内容, 保存为文件形式，并返回manual集合
    def process_bank_name(self):
        sql = "select ukey, content, content_type from crawler_manual where bank_name=%s"
        results = self.db.query(sql, self.bank_name)
        for one in results:
            ukey = one['ukey']
            content = one['content']
            content_type = one['content_type']
            if content_type == '.other':
                content_type = self.other_file_type

            filename = os.path.join(self.file_path, ukey + content_type)
            if content:
                if not os.path.exists(filename):
                    print('文件夹中没有%s, 现在保存' % filename)
                    if content_type in self.suffix_file:
                        with open(filename, 'wb') as file:
                            file.write(content)
                    else:
                        encoding = cchardet.detect(content)['encoding']
                        content = content.decode(encoding, errors='ignore')  # content从byte对象变为str对象
                        with open(filename, 'w') as file:
                            file.write(content)
            yield self.Manual(ukey=ukey, content=content, content_type=content_type)

    # 如果没有定义bank_name, 则使用start_init()方法启动
    # 自定义起点入口，可以返回一个manual_in，或者manual_in集合
    def start_init(self):
        manual_in = self.Manual(ukey='', content='', content_type='')
        yield manual_in

    def handle_manual(self, manual_in: Manual):
        ukey = manual_in.ukey
        content_type = manual_in.content_type
        filename = os.path.join(self.file_path, ukey + content_type)

        tables, text = None, None
        # ！！！此处还需再进一步补充，根据不同的文件类型，采取不同的解析方法
        if manual_in.content:
            try:
                if content_type == '.pdf':
                    tables, text = divide_pdf_tables_text(filename)
                elif content_type == '.doc' or content_type == '.docx':
                    tables, text = divide_word_tables_text(filename)
                elif content_type == '.html' or content_type == '.htm' or content_type == '.shtml' or content_type == '.shtm':
                    tables, text = divide_html_tables_text(filename)
            except Exception as e:
                self.logger.error('解析%s文件时出错：%s' % (filename, e))

        self._process_manual(ukey=ukey, tables=tables, text=text)
        return tables, text

    # 根据有没有解析出来tables判断, 记录成功和失败的次数
    def _process_manual(self, ukey, tables, text):
        if tables:
            if len(tables) > 0:
                self.success_counts += 1
                self.process_parse(ukey, self.bank_level, tables, text)
            else:
                self.failed_counts += 1
                self.process_failed(ukey, self.bank_level, tables, text)

    # 根据每家银行不同的产品说明书格式，再进一步自定义各自的从产品说明书中提取内容的操作代码
    # !!!! 子类中需要重写该方法
    def process_parse(self, ukey, bank_level, tables, text):
        # !!!更新MySQL数据库中的相应记录的状态status为done
        pass

    def process_failed(self, ukey, bank_level, tables, text):
        self.logger.error('%s的产品说明书解析不成功' % ukey)
        pass

    # 为队列queue的消费者，从队列中取出handle_manual(manual_in)方法并执行， 返回值是tables，text
    async def start_worker(self):
        while True:
            request_item = await self.queue.get()
            self.worker_tasks.append(request_item)
            if self.queue.empty():
                results = await asyncio.gather(*self.worker_tasks, return_exceptions=True)
                for task_result in results:
                    if not isinstance(task_result, RuntimeError) and task_result:
                        tables, text = task_result
                self.worker_tasks = []          # 执行完本轮任务后，self.worker_tasks重新还原为空集合
            self.queue.task_done()              # 每当消费协程调用 task_done() 表示这个条目item已经被回收，该条目所有工作已经完成，未完成计数就会减少。

    async def stop(self, _signal):
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
        await asyncio.gather(*tasks, return_exceptions=True)


