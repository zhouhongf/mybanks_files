import time


class DocumentUrl(object):

    def __init__(self, ukey: str, url: str, html_type: str, create_time: str = None, crawl_status: str = None):
        self._id = ukey
        self._url = url
        self._html_type = html_type
        self._create_time = create_time if create_time else time.strftime('%Y-%m-%d %H:%M:%S')
        self._crawl_status = crawl_status if crawl_status else 'undo'

    def __repr__(self):
        return f"【id: {self._id}, url: {self._url}, html_type: {self._html_type}, 'create_time': {self._create_time},  'crawl_status': {self._crawl_status}】"

    def do_dict_data(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            data[name] = getattr(self, name, None)
        # 为了保存进mongodb，所以将id改为_id
        data.pop('id')
        data['_id'] = self.id
        return data

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def html_type(self):
        return self._html_type

    @html_type.setter
    def html_type(self, value):
        self._html_type = value

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, value):
        self._create_time = value

    @property
    def crawl_status(self):
        return self._crawl_status

    @crawl_status.setter
    def crawl_status(self, value):
        self._crawl_status = value
