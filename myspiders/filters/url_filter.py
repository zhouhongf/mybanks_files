import re
from urllib.parse import urlparse, urljoin, urlunparse


p_tag_a = re.compile(r'<a[^>]*?href=[\'"]?([^> \'"]+)[^>]*?>(.*?)</a>', re.I | re.S | re.M)

g_doc_suffix = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf']
g_jpg_suffix = ['.jpg', '.png', '.bmp', '.jpeg', '.gif']
g_avi_suffix = ['.flv', '.mp4', '.avi', '.wmv', '.mkv']
g_htm_suffix = ['.html', '.htm', '.shtml', '.shtm']
g_exe_suffix = ['.exe', '.apk']
g_zip_suffix = ['.zip', '.rar', '.tar', '.bz2', '.7z', '.gz']


def extract_links_re(url, html):
    newlinks = set()
    # 根据<a>的正则表达式，从html中搜索出全部的<a>
    aa = p_tag_a.findall(html)
    for a in aa:
        link = a[0].strip()  # a[0]是正则表达式第1个括号内的内容，即链接，a[1]即正则表达式第2个括号内的内容，即名称
        if not link:
            continue
        link = urljoin(url, link)
        link = clean_url(link)
        if not link:
            continue
        newlinks.add(link)
    return newlinks


# 按照设定的规则，过滤出来需要的url链接
def clean_url(url):
    # 1. 是否为合法的http url
    if not url.startswith('http'):
        return ''
    # 2. 去掉静态化url后面的参数
    for np in g_htm_suffix:
        p = url.find(np)
        if p > -1:
            p = url.find('?')
            url = url[:p]
            return url
    # 3. 不下载二进制类内容的链接
    up = urlparse(url)
    path = up.path
    if not path:
        path = '/'
    postfix = path.split('.')[-1].lower()
    if postfix in g_zip_suffix:
        return ''

    # 4. 去掉标识流量来源的参数
    # badquery = ['spm', 'utm_source', 'utm_source', 'utm_medium', 'utm_campaign']
    good_queries = []
    for query in up.query.split('&'):
        qv = query.split('=')
        if qv[0].startswith('spm') or qv[0].startswith('utm_'):
            continue
        if len(qv) == 1:
            continue
        good_queries.append(query)
    query = '&'.join(good_queries)
    url = urlunparse((
        up.scheme,
        up.netloc,
        path,
        up.params,
        query,
        ''  # crawler do not care fragment
    ))
    return url
