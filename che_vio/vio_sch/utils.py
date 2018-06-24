import time
import hashlib
import json
import urllib.request


# 从车轮接口查询违章数据
def get_vio_from_chelun(v_number, v_type, v_code, e_code):
    """
    调用车轮接口查询违章
    :param v_number: 车牌号e_code
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :return: 违章数据, json格式
    """
    # 查询接口url
    url = 'http://api-cwz.eclicks.cn/partner/query'

    # 构造查询数据
    appid = '10070'                     # 账号
    app_secret = 'yacny5zgcz9id8gk'     # 密码

    timestamp = int(time.time())
    sign = hashlib.sha256(('%s%d%s' % (appid, timestamp, app_secret)).encode('utf-8')).hexdigest()

    data = {'appid': appid, 'carno': v_number, 'cartype': v_type, 'vcode': v_code, 'ecode': e_code,
            'timestamp': timestamp, 'sign': sign}

    # url转码
    data = urllib.parse.urlencode(data)

    # 构造get请求url
    url = '%s?%s' % (url, data)

    # 创建request请求
    request = urllib.request.Request(url)

    # 获得response
    response = urllib.request.urlopen(request)

    return json.loads(response.read().decode('utf-8'))


# 从典典接口查询违章数据
def get_vio_from_ddyc(v_number, v_type, v_code, e_code, city):
    """
    调用典典接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :param city: 查询城市
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
    response = urllib.request.urlopen(request)

    return json.loads(response.read().decode('utf-8'))


# 通过典典接口查询结果构造标准返回数据
def vio_dic_for_ddyc(v_number, data):
    """
    通过典典接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 车轮接口返回数据, dict
    :return: 车八佰违章数据, dict
    """
    if data['success']:
        status = 0

        vio_list = []
        for vio in data['data']['violations']:
            vio_data = {
                'time': vio['time'],
                'position': vio['address'],
                'activity': vio['reason'],
                'point': vio['point'],
                'money': vio['fine'],
                'code': vio['violationNum'],
                'location': vio['violationCity']
            }

            vio_list.append(vio_data)

        vio_dict = {'vehicleNumber': v_number, 'status': status, 'data': vio_list}
    else:
        vio_dict = {'vehicleNumber': v_number, 'status': 21}  # 查询失败

    return vio_dict


# 通过车轮接口查询结果构造标准返回数据
def vio_dic_for_chelun(v_number, data):
    """
    通过车轮接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 车轮接口返回数据, dict
    :return: 车八佰违章数据, dict
    """
    if data['code'] == 0:
        status = 0

        vio_list = []
        for vio in data['data']:
            vio_data = {
                'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(vio['date']))),
                'position': vio['address'],
                'activity': vio['detail'],
                'point': vio['point'],
                'money': vio['money'],
                'code': '',
                'location': vio['office_name']
            }

            vio_list.append(vio_data)

        vio_dict = {'vehicleNumber': v_number, 'status': status, 'data': vio_list}
    else:
        vio_dict = {'vehicleNumber': v_number, 'status': 21}  # 查询失败

    return vio_dict


if __name__ == '__main__':
    carno = '京HD95961'
    cartype = '02'
    vcode = 'LGBF5AE00HR276883'
    ecode = '751757V111111'
    car2 = {'v_number': '沪AUT715', 'v_type': '02', 'v_code': 'LSKG4AC12FA411099', 'e_code': 'H1SF1220128'}
    response_data = get_vio_from_chelun(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])

    # response_data = get_vio_from_ddyc(v_number=carno, v_type=cartype, v_code=vcode, e_code=ecode, city='')
    print(response_data)

    # v_data = vio_dic_for_ddyc(carno, response_data)
    v_data = vio_dic_for_chelun(car2['v_number'], response_data)
    print(v_data)
