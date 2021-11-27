import re


class Test(object):
    '''
    这是内容介绍
    '''
    pattern_code = re.compile(r'[产品代码编号为是：:\s]*([A-Za-z0-9][-+A-Za-z0-9]+)')
    pattern_name = '这是测试的name'

    def __init__(
        self,
        ukey: str = None,
        name: str = None,
        code: str = None,
    ):
        self._ukey = ukey
        self._name = name
        self._code = code

    def __repr__(self):
        return f"【ukey: {self._ukey},  name: {self._name}, code: {self._code}】"

    def extract_code(self, value: str):
        print('这是extract_code()输入的值:', value)
        print('这是extract_code()自带的pattern_code类属性值：', self.pattern_code)

    def extract_name(self, value: str):
        print('这是extract_name()输入的值:', value)
        print('这是extract_name()自带的pattern_code类属性值：', self.pattern_code)

    def do_test(self):
        method = getattr(self, 'extract_' + 'code', None)
        method('1234567890ASDFGHJKL')

    @property
    def ukey(self):
        return self._ukey

    @ukey.setter
    def ukey(self, value):
        self._ukey = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

