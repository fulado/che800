import time
import json
import base64
import hashlib
import pymongo

from .models import UserInfo


# 获得MongoDB数据库连接
def get_db():
    try:
        # mongodb数据库ip, 端口
        mongodb_ip = '192.168.100.234'
        mongodb_port = 27017

        # 创建连接对象
        client = pymongo.MongoClient(host=mongodb_ip, port=mongodb_port)

        # 获得数据库
        vio_db = client.violation

        return vio_db
    except Exception as e:
        print(e)
        raise e


# 校验用户信息
def check_user(param):

    # ip白名单
    # if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
    #     user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    # else:
    #     user_ip = request.META['REMOTE_ADDR']

    if param == '':
        response_data = {'status': 15, 'message': '无效请求'}
        return response_data

    try:
        param = decode_data(param)
    except Exception as e:
        print(e)
        response_data = {'status': 16, 'message': '请求参数错误'}
        return response_data

    # print(param)
    try:
        # 获取用户名和密码
        username = param['userId']
        user_token = param['token']

        # 对比用户和密码
        user = UserInfo.objects.get(username=username)
    except Exception as e:
        print(e)
        response_data = {'status': 11, 'message': '用户未登录'}
        return response_data

    # 判断token是否过期
    current_timestamp = int(time.time())

    if current_timestamp - user.timestamp > 3600:
        response_data = {'status': 17, 'message': 'token已过期'}
        return response_data

    # 计算token
    token = '%s%d%s' % (username, user.timestamp, user.password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()

    # 对比token
    if token != user_token:
        response_data = {'status': 18, 'message': 'token错误'}
        return response_data

    response_data = {'status': 0, 'param': '校验通过'}
    return response_data


# 构造返回数据
def create_response_data(data):
    response_data = base64.b64encode(json.dumps(data).encode('utf-8'))

    return response_data


# 参数解密
def decode_data(data):
    data = json.loads(base64.b64decode(data).decode('utf-8').replace('\'', '\"'))

    return data
