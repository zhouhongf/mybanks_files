# 爬虫Server，派发url给各个client去下载，根据下载成功与否，更新url状态
from sanic import Sanic
from sanic import response
import os
from pool.url_pool import UrlPool
from database.backends import MongoDatabase

print('=================================已运行URL_SERVER==============================================')

urlpool = UrlPool(os.path.abspath(__file__))  # 显示绝对路径文件名D:\MasterPython\produce\mybanks_files\url_server.py
# urlpool = UrlPool(__file__)                 # 仅显示url_server.py文件名
hub_hosts = set()
hub_urls = []

db = MongoDatabase().db()
collection_url = db['MANUAL_URL']


# 初始化Sanic, app名称为url_server
app = Sanic(__name__)


@app.listener('after_server_stop')
async def cache_urlpool(app, loop):
    global urlpool
    print('【在after_server_stop后缓存urlpool】')
    del urlpool
    print('【bye! urlpool】')
    results = collection_url.find({'crawl_status': 'pending'})
    for one in results:
        ukey = one['_id']
        one['crawl_status'] = 'undo'
        collection_url.update_one({'_id': ukey}, {'$set': one})
    print('【服务器停止前，将所有pending状态的，更新为undo状态】')


@app.route('/fileurls')
async def task_get(request):
    count = request.args.get('count', 1000)
    count = int(count)
    bank_name = request.args.get('bank', '')
    if bank_name:
        pattern_bank_name = bank_name + '=.+'
        select_list = [{'$match': {'crawl_status': 'undo', '_id': {'$regex': pattern_bank_name}}}, {'$sample': {'size': count}}]
    else:
        select_list = [{'$match': {'crawl_status': 'undo'}}, {'$sample': {'size': count}}]

    task_list = []
    results = collection_url.aggregate(select_list)
    for one in results:
        ukey = one['_id']
        url = one['url']
        if url:
            task = {'ukey': ukey, 'url': url}
            task_list.append(task)
            # 更新数据库中分发出去的记录为pending状态
            one['crawl_status'] = 'pending'
            collection_url.update_one({'_id': ukey}, {'$set': one})
    return response.json(task_list)


@app.route('/fileurls', methods=['POST', ])
async def task_post(request):
    one = request.json
    ukey = one['ukey']
    status_code = int(one['status_code'])
    if status_code == 200:
        crawl_status = 'done'
    else:
        crawl_status = 'undo'
    result = collection_url.find_one({'_id': ukey})
    result['crawl_status'] = crawl_status
    collection_url.update_one({'_id': ukey}, {'$set': result})
    print('【server收到返回，已更新状态: %s】' % one)
    return response.text('ok')


# 返回下载产品说明书文件url中提取出来的host名称，譬如浦发银行的per.spdb.com.cn
@app.route('/hubs')
async def hubs_get(request):
    global hub_hosts
    if len(hub_hosts) > 0:
        result = {'msg': 'ok', 'data': hub_hosts}
    else:
        result = {'msg': 'no', 'data': ''}
    return response.json(result)

# url_client向url_server获取任务，每次默认获取10个任务
@app.route('/task')
async def task_get(request):
    count = request.args.get('count', 10)
    try:
        count = int(count)
    except:
        count = 10
    hub_urls_count = urlpool.pop(count)     # 从urlpool中取出相应数量的任务
    return response.json(hub_urls_count)


@app.route('/task', methods=['POST', ])
async def task_post(request):
    result = request.json

    # 在网址池中设置该url的状态。
    urlpool.set_status(result['url'], result['status'])
    # 如果是重定向的url，则在网址池中设置重定向url的状态
    if result['url_real'] != result['url']:
        urlpool.set_status(result['url_real'], result['status'])

    # 向urlpool中添加新的链接，即newurls
    if result['newurls']:
        print('【receive URLs: %s】' % len(result['newurls']))
        for url in result['newurls']:
            urlpool.add(url)
    return response.text('ok')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9010, debug=False, access_log=False, workers=1)




