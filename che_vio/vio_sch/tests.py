from django.test import TestCase
import urllib
import time
import hashlib
import json


# Create your tests here.
# 查询违章: 车轮接口
def get_vio_from_chelun(carno, cartype, vcode, ecode):
    # 查询url
    url = 'http://api-cwz.eclicks.cn/partner/query'

    # 构造查询数据
    appid = '10070'
    app_secret = 'yacny5zgcz9id8gk'

    timestamp = int(time.time())
    sign = hashlib.sha256(('%s%d%s' % (appid, timestamp, app_secret)).encode('utf-8')).hexdigest()

    data = {'appid': appid, 'carno': carno, 'cartype': cartype, 'vcode': vcode, 'ecode': ecode,
            'timestamp': timestamp, 'sign': sign}
    print(data)

    # url转码
    data = urllib.parse.urlencode(data)
    print(data)

    # 构造get请求url
    url = '%s?%s' % (url, data)
    print(url)

    # 创建request请求
    request = urllib.request.Request(url)

    # 获得response
    response = urllib.request.urlopen(request)

    return json.loads(response.read().decode('utf-8'))


# 查询违章: 典典接口
def get_vio_from_ddyc(carno, cartype, vcode, ecode):
    # 查询url
    url = 'https://openapi.ddyc.com/violation/query/1.0'
    # url = 'http://openapi.ddyc.com/sign/test'
    # url = 'http://openapi.ddyc.com/violation/query'

    # 构造查询数据
    app_key = 'X9N7TKSN9JXGBAJ0'
    app_secret = '5KKVT1X1LAB9ILIQ3EJPQGGI3Q5FWB7W'

    timestamp = int(time.time() * 1000)
    # timestamp = 1483588771626
    print(timestamp)

    param = {'plateNumber': carno, 'carType': cartype, 'engineNo': ecode, 'vin': vcode}
    # param = {'plateNumber': carno, 'phone': '', 'vin': vcode, 'city': '', 'engineNo': ecode}
    param = json.dumps(param).replace(' ', '')

    sign = "%s%sapp_key=%s&timestamp=%d%s" % (app_key, app_secret, app_key, timestamp, param)
    sign = sign[::-1]
    sign = hashlib.md5(sign.encode('utf-8')).hexdigest().upper()
    print(sign)

    url = '%s?app_key=%s&timestamp=%d&sign=%s' % (url, app_key, timestamp, sign)
    print(url)

    request_data = {'plateNumber': carno, 'carType': cartype, 'engineNo': ecode, 'vin': vcode}
    request_data = json.dumps(request_data).replace(' ', '').encode('utf-8')
    print(request_data)

    # 请求头
    headers = {'Content-type': 'application/json'}

    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=request_data)

    # 获得response
    response_data = urllib.request.urlopen(request)

    return json.loads(response_data.read().decode('utf-8'))


# 从典典接口查询违章数据
def get_vio_from_ddyc2(v_number, v_type, v_code, e_code):
    """
    调用典典接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :return: 违章数据, json格式
    """
    # 查询接口url
    url = 'https://openapi.ddyc.com/violation/query/1.0'

    # 构造查询数据
    app_key = 'X9N7TKSN9JXGBAJ0'                        # 账号
    app_secret = '5KKVT1X1LAB9ILIQ3EJPQGGI3Q5FWB7W'     # 密码

    timestamp = int(time.time() * 1000)                 # 时间戳

    # 构造查询数据
    data = {'plateNumber': v_number, 'carType': v_type, 'engineNo': e_code, 'vin': v_code}
    data = json.dumps(data).replace(' ', '')

    # 构造sign
    sign = "%s%sapp_key=%s&timestamp=%d%s" % (app_key, app_secret, app_key, timestamp, data)
    sign = sign[::-1]
    sign = hashlib.md5(sign.encode('utf-8')).hexdigest().upper()

    # 构造完整查询url
    url = '%s?app_key=%s&timestamp=%d&sign=%s' % (url, app_key, timestamp, sign)

    # 请求头
    headers = {'Content-type': 'application/json'}

    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=data.encode('utf-8'))

    # 获得response
    response_data = urllib.request.urlopen(request)

    return json.loads(response_data.read().decode('utf-8'))


def get_vio_from_ddyc3(v_number, v_type, v_code, e_code, city):
    """
    调用典典接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :return: 违章数据, json格式
    """
    # 查询接口url
    url = 'https://openapi.ddyc.com/violation/query/1.0'

    # 构造查询数据
    app_key = 'X9N7TKSN9JXGBAJ0'                        # 账号
    app_secret = '5KKVT1X1LAB9ILIQ3EJPQGGI3Q5FWB7W'     # 密码

    timestamp = int(time.time() * 1000)                 # 时间戳

    # 构造查询数据
    data = {'plateNumber': v_number, 'carType': v_type, 'engineNo': e_code, 'vin': v_code, 'city': city}
    data = json.dumps(data).replace(' ', '')

    # 构造sign
    sign = "%s%sapp_key=%s&timestamp=%d%s" % (app_key, app_secret, app_key, timestamp, data)
    sign = sign[::-1]
    sign = hashlib.md5(sign.encode('utf-8')).hexdigest().upper()

    # 构造完整查询url
    url = '%s?app_key=%s&timestamp=%d&sign=%s' % (url, app_key, timestamp, sign)

    # 请求头
    headers = {'Content-type': 'application/json'}

    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=data.encode('utf-8'))

    # 获得response
    response_data = urllib.request.urlopen(request)

    return json.loads(response_data.read().decode('utf-8'))


if __name__ == '__main__':
    car1 = {'v_number': '京HD9596', 'v_type': '02', 'v_code': 'LGBF5AE00HR276883', 'e_code': '751757V'}
    car2 = {'v_number': '沪AUT715', 'v_type': '02', 'v_code': 'LSKG4AC12FA411099', 'e_code': 'H1SF1220128'}

    response_data = get_vio_from_chelun(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])

    # response_data = get_vio_from_ddyc2(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])

    print(response_data)
