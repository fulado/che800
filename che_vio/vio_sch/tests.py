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

    sign = "%s%sapp_key=%s津RCZ178&timestamp=%d%s" % (app_key, app_secret, app_key, timestamp, param)
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
    # 0707f5a313c02f9962dfc5ee76dca41a
    # timestamp = 1547453000
    car_type = v_type
    area = v_number[0]

    cypo_password = hashlib.md5(password.encode()).hexdigest().upper()

    sign = username + cypo_password + v_number + e_code + v_code + car_type + area + str(timestamp)

    sign = hashlib.md5(sign.encode()).hexdigest()

    print(timestamp)
    print(sign)

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


# 通过少帅接口查询结果构造标准返回数据
def vio_dic_for_shaoshuai(v_number, data):
    """
    通过少帅接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 少帅接口返回数据, dict
    :return: 车八佰违章数据, dict
    """

    if 'state' in data and 'success' in data['state']:
        status = 0

        vio_list = []
        if 'result' in data and 'historys' in data['result']:
            for vio in data['result']['historys']:
                # 缴费状态
                try:
                    if 'fine_status' in vio:
                        if '未缴款' in vio['fine_status']:
                            vio_pay = 0
                        elif '已缴款' in vio['fine_status']:
                            vio_pay = 1
                        else:
                            vio_pay = -1
                    else:
                        vio_pay = -1
                except Exception as e:
                    print(e)
                    vio_pay = -1

                # 已经缴费的违章数据不再返回
                if vio_pay == 1:
                    continue

                # 违法时间
                if 'occur_date' in vio:
                    vio_time = vio['occur_date']
                else:
                    vio_time = ''

                # 违法地点
                if 'occur_area' in vio:
                    vio_address = vio['occur_area']
                else:
                    vio_address = ''

                # 违法行为
                if 'info' in vio:
                    vio_activity = vio['info']
                else:
                    vio_activity = ''

                # 扣分
                if 'fen' in vio:
                    vio_point = str(vio['fen'])
                else:
                    vio_point = ''

                # 罚款
                if 'money' in vio:
                    vio_money = str(vio['money'])
                else:
                    vio_money = ''

                # 违法代码
                if 'illegal_code' in vio:
                    vio_code = vio['illegal_code']
                else:
                    vio_code = ''

                # 处理机关
                if 'officer' in vio:
                    vio_loc = vio['officer']
                else:
                    vio_loc = ''

                # 处理状态
                try:
                    if 'fine_status' in vio:
                        if '未处理' in vio['fine_status']:
                            vio_deal = 0
                        elif '已处理' in vio['fine_status']:
                            vio_deal = 1
                        else:
                            vio_deal = -1
                    else:
                        vio_deal = -1
                except Exception as e:
                    print(e)
                    vio_deal = -1

                vio_data = {
                    'time': vio_time,
                    'position': vio_address,
                    'activity': vio_activity,
                    'point': vio_point,
                    'money': vio_money,
                    'code': vio_code,
                    'location': vio_loc,
                    'deal': vio_deal,
                    'pay': vio_pay
                }

                vio_list.append(vio_data)

        vio_dict = {'vehicleNumber': v_number, 'status': status, 'data': vio_list}
    else:
        if 'error_code' in data and 'error_message' in data:
            return get_status(data['error_code'], 6)
        else:
            return {'status': 53, 'msg': '查询失败'}

    return vio_dict


# 根据少帅接口的返回状态码构造本地平台返回给用户的状态码
def create_status_from_shaoshuai(origin_status):
    if origin_status == 50016:
        status = 32
        msg = '车牌号或车辆类型错误'
    elif origin_status == 50200:
        status = 36
        msg = '车辆信息不正确'
    else:
        status = 51
        msg = '数据源异常'

    return {'status': status, 'msg': msg}


if __name__ == '__main__':
    # car2 = {'v_number': '京HD9596', 'v_type': '02', 'v_code': 'LGBF5AE00HR276883', 'e_code': '751757V'}
    # car2 = {'v_number': '苏AQ6R59', 'v_type': '02', 'v_code': 'LSGUD84X3FE009951', 'e_code': '150330725'}
    # car2 = {'v_number': '沪E59583', 'v_type': '02', 'v_code': 'LTVBJ874960003131', 'e_code': '5GRC044604'}
    # car2 = {'v_number': '沪AYC335', 'v_type': '02', 'v_code': 'LSKG4AC11FA413877', 'e_code': 'H1SF5250141'}
    # car2 = {'v_number': '陕AS71N5', 'v_type': '02', 'v_code': 'LSVNB418XGN043525', 'e_code': '480843'}
    # car2 = {'v_number': '沪ABT031', 'v_type': '02', 'v_code': '', 'e_code': '132111162'}
    car2 = {'v_number': '冀A173SZ', 'v_type': '02', 'v_code': 'LJDLAA293D0223021', 'e_code': 'D5566502'}
    #
    response_data = get_vio_from_chelun(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])
    #
    # response_data = get_vio_from_ddyc2(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])
    pprint(response_data)
    #
    # response_data = vio_dic_for_shaoshuai(car2['v_number'], response_data)
    # pprint(response_data)

    # create_sign('test', 'test')
    # create_sign('pingan3', 'pingan3_init')

    # q = queue.Queue(maxsize=5)
    # for i in range(10):
    #     t = MyThread(i)
    #     q.put(t)
    #     t.start()
    #
    # print('end')

    # backup()
