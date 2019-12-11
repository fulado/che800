import time
import json
import hashlib
import urllib.request


# 从懂云接口查询数据
def get_vio_from_doyun(v_number, v_type, v_code, e_code, city):
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
    print(url)
    print(data.encode())
    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=data.encode('utf-8'))

    # 获得response
    response_data = urllib.request.urlopen(request)

    return json.loads(response_data.read().decode('utf-8'))


if __name__ == '__main__':
    car2 = {'v_number': '沪H31092', 'v_type': '02', 'v_code': 'LFV4A24F383049673', 'e_code': '171809'}
    response_data = get_vio_from_doyun(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'], '')
