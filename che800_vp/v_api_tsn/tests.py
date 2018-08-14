from django.test import TestCase
import urllib
import base64
import json
# import pymongo
import time
import hashlib
import pymysql
from pprint import pprint


class ViolationException(Exception):
    def __str__(self):
        return 'violation research error'


def get_token():
    data = str({"username": 'test_old', 'password': 'test_old'})
    # url = 'http://47.94.18.47/IllegalData-search/login'
    url = 'http://127.0.0.1:8000/login'
    # url = 'http://vio.che800.cc/login'
    data = get_json(get_response_encoded_data(url, data))
    print(data)
    return data['token']


def get_violation(car_list):
    # url = 'http://47.94.18.47/IllegalData-search/vehicle'
    url = 'http://127.0.0.1:8000/illegal'
    # url = 'http://vio.che800.cc/illegal'

    token = get_token()
    data = json.dumps({'userId': 'test_old', 'token': token, 'cars': car_list})
    # print(data)
    data = get_response_encoded_data(url, data)
    # print(data)
    if b'\xef\xbf\xbd' in data:
        raise ViolationException()

    return get_json(data)


def register_vehicle(car_list):
    # url = 'http://47.94.18.47/IllegalData-search/vehicle'
    # url = 'http://127.0.0.1:8000/register'
    url = 'http://vio.che800.cc/register'

    token = get_token()
    data = json.dumps({'userId': 'test0011', 'token': token, 'cars': car_list, 'worktype': '2'})
    # print(data)
    data = get_response_encoded_data(url, data)

    return get_json(data)


def get_response_encoded_data(url, data):
    # base64加密
    data = base64.b64encode(data.encode('utf-8'))
    data = 'param=%s' % data.decode('utf-8')
    # print(data)

    request = urllib.request.Request(url, data.encode('utf-8'))

    response = urllib.request.urlopen(request)

    return base64.b64decode(response.read())


def get_json(data):
    data = data.decode('utf-8')
    return json.loads(data)


def get_violation_count(cars):
    try:
        data = get_violation(cars)
        print(data)
        data = data['result']
        violation_dict = {}
        for violation_data in data:
            # print(violation_data)
            if violation_data['status'] == 0:
                number = violation_data['platNumber']
                violation_count = len(violation_data['punishs'])
                violation_dict[number] = violation_count
        return violation_dict
    except Exception as violation_error:
        raise violation_error
        return None


# 根据车牌查询违章
def get_violation_from_mongo():
    try:
        # 创建连接对象
        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        # 获得数据库
        db = client.violation
        # 查询多条文档
        result = db.ViolationUp.find({'hphm': "津MHR138"})
        print(result.count())
        if result:
            print('True')
        else:
            print('False')

        for item in result:
            print('%s, %s, %s' % (item['hphm'], item['wfsj'], item['wfdz']))
    except Exception as e:
        print(e)


# 测试天津违章查询接口
def test_tsn_vio(vehicle_number, vehicle_type):
    # 构造查询数据
    username = 'test'
    password = 'test'
    timestamp = int(time.time())
    sign = hashlib.sha1(('%s%d%s' % (username, timestamp, password)).encode('utf-8')).hexdigest()

    data = {'username': username, 'timestamp': timestamp, 'sign': sign, 'vehicleNumber': vehicle_number,
            'vehicleType': vehicle_type}

    # url转码
    data = urllib.parse.urlencode(data)

    # 接口地址
    url = 'http://111.160.75.92:9528/violation'
    request = urllib.request.Request(url, data.encode())

    response = urllib.request.urlopen(request)

    return response.read()


# 生成查询sign
def create_sign(username, password):
    # password = hashlib.sha1(password.encode('utf_8')).hexdigest().upper()
    timestamp = int(time.time())
    sign = '%s%d%s' % (username, timestamp, password)
    sign = hashlib.sha1(sign.encode('utf_8')).hexdigest()

    print(timestamp)
    print(sign)


# 从mysql数据中读取车辆信息
def test_vio_query():

    token = get_token()

    # 创建数据库连接
    host = '127.0.0.1'
    password = 'xiaobai'
    port = 3306
    user = 'root'
    database = 'test'
    charset = 'utf8mb4'

    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

    # 获取Cursor对象
    cs = conn.cursor()

    # 执行sql语句
    count = cs.execute('select * from vehicle')

    for i in range(count):
        result = cs.fetchone()
        cars = create_car_list(result)

        vio_data = get_violation_2(cars, token)
        print(i)
        print(vio_data)

    cs.close()
    conn.close()


def create_car_list(car_info):
    cars = [{'engineNumber': car_info[4],
             'platNumber': car_info[1],
             'carType': car_info[2],
             'vinNumber': car_info[3]}]

    return cars


def get_violation_2(car_list, token):
    # url = 'http://47.94.18.47/IllegalData-search/vehicle'
    # url = 'http://127.0.0.1:8000/illegal'
    # url = 'http://vio.che800.cc/illegal'

    data = json.dumps({'userId': 'test_old', 'token': token, 'cars': car_list})
    # print(data)
    data = get_response_encoded_data(url, data)

    return get_json(data)


if __name__ == '__main__':
    # cars = [{'engineNumber': '171531132',
    #          'platNumber': '川A2P73T',
    #          'carType': '02',
    #          'vinNumber': 'LSGBL5440HF090533'}]

    # cars = [{'engineNumber': 'H1SF5210072',
    #          'platNumber': '沪AYC967',
    #          'carType': '02',
    #          'vinNumber': 'LSKG4AC1XFA413599'}]

    # cars = [{'engineNumber': '751757V',
    #          'platNumber': '京HD9596',
    #          'carType': '02',
    #          'vinNumber': 'LGBF5AE00HR276883',
    #          # 'workCity': '上海',
    #          }]

    # cars = [{'engineNumber': 'H17079',
    #          'platNumber': '津CC825',
    #          'carType': '16',
    #          'vinNumber': '564847'}]

    # cars = [{'engineNumber': '12345678901',
    #          'platNumber': '国A88888',
    #          'carType': '02',
    #          'vinNumber': 'ABCDEFG1232'}]

    # cars = [{'engineNumber': '7A3484',
    #          'platNumber': '浙A3MF93',
    #          'carType': '02',
    #          'vinNumber': 'LSVXZ25N2G2144262'}]

    # cars = [{'engineNumber': '27682130045069',
    #          'platNumber': '津DXV189',
    #          'carType': '02',
    #          'vinNumber': 'LSGLP83X5HF027899'}]
    #
    # try:
    #     violation_data = get_violation(cars)
    #     # violation_data = register_vehicle(cars)
    #     pprint(violation_data)
    # except Exception as e:
    #     print(e)

    # get_violation_from_mongo()
    # vehicle_number = '津NWX388'
    # vehicle_type = '02'
    #
    # start_time = time.time()
    # for i in range(10):
    #     response_data = test_tsn_vio(vehicle_number, vehicle_type)
    #     # print(i, ' ')
    # end_time = time.time()
    #
    # print(json.loads(response_data.decode('utf-8')))
    # print(end_time - start_time)

    create_sign('test', 'test')

    # get_token()

    # test_vio_query()

    """
    {'feedback': {'cars': '沪AYC967', 'requestIp': '47.94.18.47', 'responseTime': '2018-07-11 19:31:39'}, 'result': {'platNumber': '沪AYC967', 'punishs': [{'reason': '驾驶中型以上载客载货汽车、危险物品运输车辆以外的其他机动车行驶超过规定时速10%未达20%的', 'paystat': '1', 'viocjjg': '和静县公安局交警大队', 'punishPoint': '3', 'location': '国道218线575公里300米', 'state': '1', 'time': '2017-07-29 12:44:00', 'punishMoney': '200'}, {'reason': '驾驶中型以上载客载货汽车、校车、危险物品运输车辆以外的其他机动车行驶超过规定时速20%以上未达到50%的', 'paystat': '1', 'viocjjg': '吉木乃县交通警察大队', 'punishPoint': '6', 'location': '国道217线173公里', 'state': '1', 'time': '2018-07-03 15:28:00', 'punishMoney': '200'}], 'status': '0'}}
platNumber"""
