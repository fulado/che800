import base64
import urllib.request
import json
import time
from threading import Thread


def get_token():
    data = str({"username": 'my_test', 'password': 'my_test'})
    # url = 'http://58.87.123.72/login/shenzhou'
    # url = 'http://illegal.ethane.com.cn:20900/violation-point/login'
    # url = 'http://58.87.123.72/login'
    # url = 'http://127.0.0.1:8000/login/shenzhou'
    # url = 'http://vio.che800.cc/login'
    url = 'http://111.160.75.92:9528/violation-point/login'
    # url = 'http://127.0.0.1:8000/violation-point/login'

    data = get_json(get_response_encoded_data(url, data))
    print(data)
    return data['token']


def get_violation(car_list, token):
    # url = 'http://58.87.123.72/illegal/shenzhou'
    # url = 'http://illegal.ethane.com.cn:20900/violation-point/illgledata/vehicleDate'
    # url = 'http://58.87.123.72/illegal'
    # url = 'http://127.0.0.1:8000/illegal/shenzhou'
    # url = 'http://vio.che800.cc/illegal'
    url = 'http://111.160.75.92:9528/violation-point/illgledata/vehicleDate'
    # url = 'http://127.0.0.1:8000/violation-point/illgledata/vehicleDate'

    # token = '4589427C530383B4CAF85243E2B42DA3'
    data = json.dumps({'userId': 'my_test', 'token': token, 'cars': car_list})
    # print(data)
    data = get_response_encoded_data(url, data)
    # print(data)
    # print(get_json(data))
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


# 违章查询线程
def query_thread(car_list, token):
    while True:
        get_violation(car_list, token)
        time.sleep(5)


if __name__ == '__main__':

    cars = [{'engineNumber': '382201',
             'platNumber': '津HVR531',
             'carType': '02'}]

    # 获取token
    token = get_token()

    print(token)

    # 建100个车辆查询线程
    for i in range(500):
        print('process %d is working' % i)
        t_get_vehicle_thread = Thread(target=query_thread, args=(cars, token))
        t_get_vehicle_thread.start()
