#!/usr/bin/env python
import re
import json
from typing import Union
from lxml import etree

from .exceptions import NothingMatchedError


class BaseField(object):
    """
    BaseField class
    """

    def __init__(self, default="", many: bool = False):
        """
        Init BaseField class
        url: http://lxml.de/index.html
        :param default: default value
        :param many: if there are many fields in one page
        default: str, 设置默认值，建议定义，否则找不到字段时会报错
        many: bool, 返回值将是一个列表
        """
        self.default = default
        self.many = many

    def extract(self, *args, **kwargs):
        raise NotImplementedError("extract is not implemented.")


class _LxmlElementField(BaseField):

    def __init__(
        self,
        css_select: str = None,
        xpath_select: str = None,
        default=None,
        many: bool = False,
    ):
        """
        :param css_select: css select http://lxml.de/cssselect.html
        :param xpath_select: http://www.w3school.com.cn/xpath/index.asp
        :param default: inherit
        :param many: inherit
        __init__()方法举例：
        target_item = TextField(css_select="div.item")
        title = TextField(css_select="span.title")
        cover = AttrField(css_select="div.pic>a>img", attr="src")
        abstract = TextField(css_select="span.inq", default="")
        """
        super(_LxmlElementField, self).__init__(default=default, many=many)
        self.css_select = css_select
        self.xpath_select = xpath_select

    def _get_elements(self, *, html_etree: etree._Element):
        if self.css_select:                                           # 如果self.css_select为True, 则使用cssselect()方法来提取elements, etree会匹配所有符合条件的dom
            elements = html_etree.cssselect(self.css_select)
        elif self.xpath_select:                                       # 如果self.xpath_select为True, 则使用xpath()方法来提取elements, etree会匹配所有符合条件的dom
            elements = html_etree.xpath(self.xpath_select)
        else:
            raise ValueError(f"{self.__class__.__name__} field: css_select or xpath_select is expected")
        if not self.many:                                             # 如果self.many不为True, 则返回elements的第一个记录， 否则全部返回
            elements = elements[:1]
        return elements

    def _parse_element(self, element):
        raise NotImplementedError

    def extract(self, html_etree: etree._Element, is_source: bool = False):
        elements = self._get_elements(html_etree=html_etree)
        # 如果是target_item，则表明是一个预先提取的部分，为source
        if is_source:
            return elements if self.many else elements[0]

        # 如果不是target_item，但通过css_select或xpath_select提取出来的elements, elements为True
        if elements:
            # 则根据子类AttrField，HtmlField，TextField重写的_parse_element()方法，提取出elements集合
            results = [self._parse_element(element) for element in elements]
        elif self.default is None:
            # 如果self.default则返回错误提示：_LxmlElementField需要有selector或者default值
            raise NothingMatchedError(
                f"Extract `{self.css_select or self.xpath_select}` error, "
                f"please check selector or set parameter named `default`"
            )
        else:
            # 如果如果不是target_item，也没有通过css_select或xpath_select提取出来的elements，也没有传递进来的default值
            # 则返回default=None
            results = self.default if type(self.default) == list else [self.default]
        # 如果self.many为True, 则返回results集合，否则返回results集合中的第一个元素
        return results if self.many else results[0]


class AttrField(_LxmlElementField):
    """
    This field is used to get  attribute.
    AttrField需要一个额外的参数：
    attr：目标标签属性
    """

    def __init__(
        self,
        attr,
        css_select: str = None,
        xpath_select: str = None,
        default="",
        many: bool = False,
    ):
        super(AttrField, self).__init__(
            css_select=css_select, xpath_select=xpath_select, default=default, many=many
        )
        self.attr = attr

    def _parse_element(self, element):
        return element.get(self.attr, self.default)


class HtmlField(_LxmlElementField):
    """
    This field is used to get raw html data.
    """

    def _parse_element(self, element):
        return etree.tostring(element, encoding="utf-8").decode(encoding="utf-8")


class TextField(_LxmlElementField):
    """
    This field is used to get text.
    """

    def _parse_element(self, element):
        if isinstance(element, etree._ElementUnicodeResult):
            strings = [node for node in element]
        else:
            strings = [node.strip() for node in element.itertext()]
        string = "".join(strings)
        return string if string else self.default


class RegexField(BaseField):
    """
    This field is used to get raw html code by regular expression.
    RegexField uses standard library `re` inner, that is to say it has a better performance than _LxmlElementField.
    RegexField需要一个额外的参数：
    re_select: str, 正则表达式字符串
    """

    def __init__(self, re_select: str, re_flags=0, default="", many: bool = False):
        super(RegexField, self).__init__(default=default, many=many)
        self._re_select = re_select
        self._re_object = re.compile(self._re_select, flags=re_flags)

    def _parse_match(self, match):
        """
        If there is a group dict, return the dict;
            even if there's only one value in the dict, return a dictionary;
        If there is a group in match, return the group;
            if there is only one value in the group, return the value;
        if there has no group, return the whole matched string;
        if there are many groups, return a tuple;
        :param match:
        :return:
        """
        if not match:
            if self.default:
                return self.default
            else:
                raise NothingMatchedError(
                    f"Extract `{self._re_select}` error, "
                    f"please check selector or set parameter named `default`"
                )
        else:
            string = match.group()
            groups = match.groups()
            group_dict = match.groupdict()
            if group_dict:
                return group_dict
            if groups:
                return groups[0] if len(groups) == 1 else groups
            return string

    def extract(self, html: Union[str, etree._Element]):
        # 如果html是etree._Element实例，则将其转为string格式
        if isinstance(html, etree._Element):
            html = etree.tostring(html).decode(encoding="utf-8")
        # 如果many是True, 则多处匹配正则寻找
        if self.many:
            matches = self._re_object.finditer(html)
            return [self._parse_match(match) for match in matches]
        # 如果不是many, 则仅使用正则的search()方法寻找单处
        else:
            match = self._re_object.search(html)
            return self._parse_match(match)


class JsonField(BaseField):

    def __init__(
        self,
        json_select: str = None,
        default=None,
        many: bool = False,
    ):
        """
        :param json_select: 自创，以 '>'来split()
        :param default: inherit
        :param many: inherit
        __init__()方法举例：
        target_item = JsonField(json_select="a>b>c")
        title = JsonField(json_select="e")
        cover = JsonField(json_select="e>f>g")
        """
        super(JsonField, self).__init__(default=default, many=many)
        self.json_select = json_select

    # 根据json_select的层级数，一层一层的提取json数据，例如json_select="a>b>c"
    def _get_elements(self, jsondata: json):
        if not self.json_select:
            return self.default

        list_select = self.json_select.split('>')
        for one in list_select:
            jsondata = jsondata[one]
        return jsondata

    # 根据json_select，从json数据中，提取出值，例如title = JsonField(json_select="e")
    def extract(self, jsondata: json):
        return self._get_elements(jsondata=jsondata)





