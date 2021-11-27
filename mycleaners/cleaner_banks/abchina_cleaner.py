from mycleaners.base.cleaner import Cleaner
from mycleaners.base.manual_text_only import ManualTextOnly
import re
import pdfplumber
from collections import namedtuple
import os


class AbchinaTextOnly(ManualTextOnly):
    labels_check_config = {}


class AbchinaCleaner(Cleaner):
    name = 'AbchinaCleaner'
    bank_name = None
    Manual = namedtuple("Manual", "ukey content content_type")

    def start_init(self):
        self.bank_name = '农业银行'
        list_filenames = os.listdir(self.file_path)
        for filename in list_filenames:
            if filename.startswith(self.bank_name):
                words = os.path.splitext(filename)
                ukey = words[0]
                content_type = words[-1]
                print('开始执行start_init方法，ukey=%s, content_type=%s' % (ukey, content_type))
                manual_in = self.Manual(ukey=ukey, content='novalue', content_type=content_type)
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
                    tables, text = self.divide_pdf_tables_text(filename)
            except Exception as e:
                self.logger.error('解析%s文件时出错：%s' % (filename, e))

        self._process_manual(ukey=ukey, tables=tables, text=text)
        return tables, text


    def divide_pdf_tables_text(self, path):
        with pdfplumber.open(path) as pdf:
            tables_text = ''
            text = ''
            for page in pdf.pages:
                tables = page.find_tables()
                words = page.extract_words()
                words_left = ''
                if tables:
                    words_left_page = ''
                    for table in tables:
                        rows = table.extract()
                        for row in rows:
                            if row:
                                for ceil in row:
                                    if ceil:
                                        ceil = re.sub(r'\s+', '', ceil)
                                        tables_text += ceil

                        x0, top, x1, bottom = table.bbox
                        # 表格top数值应大于表格前面文字的最后一个字的bottom
                        # 表格bottom数值应小于表格后面文字的第一个字的top
                        for word in words:
                            if word:
                                if word['bottom'] < top:
                                    words_left_page += word['text']
                                elif word['top'] > bottom:
                                    words_left_page += word['text']
                    words_left += words_left_page
                else:
                    for word in words:
                        if word:
                            words_left += word['text']
                text += words_left
            return [tables_text], text

    def process_parse(self, ukey, tables, text):
        tables_text = tables[0]
        content = tables_text + '\t' + text
        wealth = AbchinaTextOnly.start(self.bank_name, ukey, content)
        print('解析的内容是：%s' % wealth)


def start():
    # AbchinaCleaner.start()
    pass



