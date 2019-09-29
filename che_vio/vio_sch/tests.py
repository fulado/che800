from django.test import TestCase
import urllib
import time
import hashlib
import json
import threading
import pymysql
from pprint import pprint


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


# 从车务帮接口查询数据
def get_vio_from_cwb(v_number, v_type, vin, e_code='', city=''):
    url = 'http://www.chewubang.net/api/get/fine/'

    username = "ChunBo"  # 用户名
    password = "XcJ6JeUIXMmP6bKzxigmNUuBvlVybMD2"  # 密码

    area = v_number[0] if v_number else ''
    timestamp = int(time.time())  # 当前时间10位unix时间戳

    if v_number[0] in ['陕', '琼']:
        vin = e_code

    vin = vin[-6:]

    sign = username + password + str(timestamp) + v_number + vin + v_type + area
    sign = hashlib.md5(sign.encode()).hexdigest()

    data = {
        "username": username,
        "brandType": v_type,
        "vehNumKey": vin,
        "time": timestamp,
        "carNum": v_number,
        "sign": sign,
        'area': area
    }

    response_data = requests.post(url=url, data=data)

    return json.loads(response_data.content.decode())


# 生成查询sign
def create_sign(username, password):
    password = hashlib.sha1(password.encode('utf_8')).hexdigest().upper()
    timestamp = int(time.time())
    sign = '%s%d%s' % (username, timestamp, password)
    sign = hashlib.sha1(sign.encode('utf_8')).hexdigest().upper()

    print(timestamp)
    print(sign)


# 线程测试
class MyThread(threading.Thread):
    def __init__(self, num):
        threading.Thread.__init__(self)
        self.num = num

    def run(self):
        time.sleep(1)
        print('running thread is num %d' % self.num)


# 备份表
def backup():

    # 数据库连接信息
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    password = 'xiaobai'
    database = 'violation'
    charset = 'utf8mb4'

    try:
        # 创建连接
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

        # 获取Cursor对象
        cs = conn.cursor()

        # 表名中包含的日期
        name_time = time.strftime('%Y%m%d', time.localtime())

        # 日志表改名
        sql = 'RENAME TABLE vio_sch_loginfo TO vio_sch_loginfo_%s;' % name_time
        cs.execute(sql)

        # 新建日志表
        sql = """CREATE TABLE `vio_sch_loginfo` (
                      `id` int(11) NOT NULL AUTO_INCREMENT,
                      `query_time` datetime(6) DEFAULT NULL,
                      `status` int(11) DEFAULT NULL,
                      `comments` varchar(200) DEFAULT NULL,
                      `url_id` int(11) DEFAULT NULL,
                      `user_id` int(11) DEFAULT NULL,
                      `vehicle_number` varchar(20) DEFAULT NULL,
                      `ip` varchar(20) DEFAULT NULL,
                      PRIMARY KEY (`id`),
                      FOREIGN KEY (`url_id`) REFERENCES `vio_sch_urlinfo` (`id`),
                      FOREIGN KEY (`user_id`) REFERENCES `vio_sch_userinfo` (`id`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        cs.execute(sql)

        # 违章表改名
        sql = 'RENAME TABLE vio_sch_vioinfo TO vio_sch_vioinfo_%s;' % name_time
        cs.execute(sql)

        # 新建违章表
        sql = """CREATE TABLE `vio_sch_vioinfo` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `vehicle_number` varchar(20) DEFAULT NULL,
                    `vehicle_type` varchar(10) DEFAULT NULL,
                    `vio_time` varchar(30) DEFAULT NULL,
                    `vio_position` varchar(100) DEFAULT NULL,
                    `vio_activity` varchar(100) DEFAULT NULL,
                    `vio_point` int(11) DEFAULT NULL,
                    `vio_money` int(11) DEFAULT NULL,
                    `vio_code` varchar(20) DEFAULT NULL,
                    `vio_loc` varchar(50) DEFAULT NULL,
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=6238 DEFAULT CHARSET=utf8mb4"""
        cs.execute(sql)
    except Exception as e:
        print(e)

    finally:
        # 关闭Cursor
        cs.close()

        # 关闭连接
        conn.close()


# 从盔甲获取违章数据
def get_vio_from_kuijia(v_number, v_code, e_code):

    # 构造查询数据
    data = {'plate': v_number, 'vin': v_code, 'engine': e_code}
    data = json.dumps(data)

    # 构造完整查询url
    url = 'http://git.ikuijia.com:8380/che800-api/api/peccancy/get.do'

    # 请求头
    headers = {'Content-type': 'application/json'}

    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=data.encode('utf-8'))

    # 获得response
    response_data = urllib.request.urlopen(request)

    return json.loads(response_data.read().decode('utf-8'))


# 从少帅接口获取违章数据
def get_vio_from_shaoshuai(v_number, v_type, v_code, e_code):

    # 构造查询数据
    username = 'HC'
    password = 'HC'
    timestamp = int(time.time())
    car_type = v_type
    area = v_number[0]

    cypo_password = hashlib.md5(password.encode()).hexdigest().upper()

    sign = username + cypo_password + v_number + e_code + v_code + car_type + area + str(timestamp)
    sign = hashlib.md5(sign.encode()).hexdigest()

    data = {'username': username,
            'carNum': v_number,
            'engineNumber': e_code,
            'vin': v_code,
            'carType': car_type,
            'area': area,
            'time': timestamp,
            'sign': sign
            }

    data = urllib.parse.urlencode(data)

    # 构造完整查询url
    url = 'http://119.23.239.229/IllegalQuery/user/userApi'

    # 请求头
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=data.encode())

    # 获得response
    response_data = urllib.request.urlopen(request)

    return json.loads(response_data.read().decode('utf-8'))


# 从少帅接口获取违章数据
def get_vio_from_haotong(v_number, v_type, v_code, e_code):

    # 构造查询数据
    username = 'HC_shanghai'
    password = 'HC_shanghai'
    timestamp = int(time.time())
    car_type = v_type
    area = v_number[0]

    cypo_password = hashlib.md5(password.encode()).hexdigest().upper()

    sign = username + cypo_password + v_number + e_code + v_code + car_type + area + str(timestamp)
    sign = hashlib.md5(sign.encode()).hexdigest()

    data = {'username': username,
            'carNum': v_number,
            'engineNumber': e_code,
            'vin': v_code,
            'carType': car_type,
            'area': area,
            'time': timestamp,
            'sign': sign
            }

    data = urllib.parse.urlencode(data)

    # 构造完整查询url
    url = 'http://119.23.239.229/IllegalQuery/user/userApi'

    # 请求头
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=data.encode())

    # 获得response
    response_data = urllib.request.urlopen(request)

    return json.loads(response_data.read().decode('utf-8'))



# 从懂云接口查询数据
def get_vio_from_doyun(v_number, v_type, v_code, e_code, city=''):
    """
    调用典典接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :return: 违章数据, json格式
    """
    # 查询接口url
    url = 'https://openapi.docloud.vip/violation/query/1.0'

    # 构造查询数据
    app_key = 'KSJWW7OABAMMV4VX'                        # 账号
    app_secret = 'YMPQFUKTTRIE4UA44NXN89SEEYCAIGQ7'     # 密码

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
    # car2 = {'v_number': '京HD9596', 'v_type': '02', 'v_code': 'LGBF5AE00HR276883', 'e_code': '751757V'}
    # car2 = {'v_number': '津RAV877', 'v_type': '02', 'v_code': 'LSGGJ5450JS043259', 'e_code': '173073371'}
    car2 = {'v_number': '闽DZ299M', 'v_type': '02', 'v_code': 'LSGJB84JXHY031967', 'e_code': '163084534'}
    # car2 = {'v_number': '津RPU307', 'v_type': '02', 'v_code': 'LXVD3GFC2JA014542', 'e_code': 'J014144'}
    car2 = {'v_number': '沪D77737', 'v_type': '02', 'v_code': 'LFMH65816ES002064', 'e_code': '8583791'}
    #
    # response_data = get_vio_from_shaoshuai(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])
    #
    response_data = get_vio_from_haotong(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])
    #
    pprint(response_data)

    # create_sign('ctrip', 'ctrip_init')

    # q = queue.Queue(maxsize=5)
    # for i in range(10):
    #     t = MyThread(i)
    #     q.put(t)
    #     t.start()
    #
    # print('end')

    # backup()
