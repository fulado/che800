import time
import hashlib
import json
import urllib.request
import urllib.parse
from .models import VioInfo, LogInfo, LocInfo, VehicleBackup


# 判断查询城市是否正确
def get_url_id(v_number, city):

    if city not in ['津', '天津', '天津市']:  # 目前除天津市外, 均不提供外地车查询, 如果以后开通, 可以去掉这行
        city = ''                            # 和这一行

    try:
        if city == '':
            loc_info = LocInfo.objects.get(plate_name=v_number[0])
        else:
            loc_info = LocInfo.objects.get(loc_name__contains=city)
    except Exception as e:
        print(e)
        return None, city

    return loc_info.url.id, city


# 从本地数据库查询违章
def get_vio_from_loc(v_number, v_type=2):
    try:
        vio_info_list = VioInfo.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)
    except Exception as e:
        print(e)
        return None

    # 如果有数据, 构造违章信息
    if vio_info_list:
        vio_list = []
        for vio in vio_info_list:
            # 如果没有违章直接略过
            if vio.vio_code == '999999':
                continue

            vio_data = {
                'time': vio.vio_time if vio.vio_time else '',
                'position': vio.vio_position if vio.vio_position else '',
                'activity': vio.vio_activity if vio.vio_activity else '',
                'point': str(vio.vio_point),
                'money': str(vio.vio_money),
                'code': vio.vio_code if vio.vio_code else '',
                'location': vio.vio_loc if vio.vio_loc else '',
                'deal': str(vio.deal_status),
                'pay': str(vio.pay_status)
            }

            vio_list.append(vio_data)
        # print('%s -- local db' % v_number)

        return {'vehicleNumber': v_number, 'status': 0, 'data': vio_list}
    else:
        return None


# 从天津接口查询违章数据
def get_vio_from_tj(v_number, v_type, e_code):
    """
    从天津接口查询违章数据
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param e_code: 发动机号
    :return: 违章数据, json格式
    """
    # 查询接口rul
    url = 'http://111.160.75.92:9528/violation'

    # 构造查询数据
    username = 'test'
    password = 'test'
    timestamp = int(time.time())
    sign = hashlib.sha1(('%s%d%s' % (username, timestamp, password)).encode('utf-8')).hexdigest()

    data = {'username': username, 'timestamp': timestamp, 'sign': sign, 'vehicleNumber': v_number,
            'vehicleType': v_type, 'engineCode': e_code}

    # url转码
    data = urllib.parse.urlencode(data)

    # 创建request请求
    request = urllib.request.Request(url, data.encode())

    # 获得response
    response = urllib.request.urlopen(request)

    return json.loads(response.read().decode('utf-8'))


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


# 从盔甲接口查询违章数据
def get_vio_from_kuijia(v_number, v_code, e_code):

    # 查询url
    url = 'http://git.ikuijia.com:8380/che800-api/api/peccancy/get.do'

    # 构造查询数据
    data = {'plate': v_number, 'vin': v_code, 'engine': e_code}
    data = json.dumps(data)

    # 请求头
    headers = {'Content-type': 'application/json'}

    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=data.encode('utf-8'))

    # 获得response
    response = urllib.request.urlopen(request)

    return json.loads(response.read().decode('utf-8'))


# 从zfb接口查询违章数据
def get_vio_from_zfb(v_number, v_type, v_code, e_code):

    # 查询url
    url = 'https://zfbservice.xmxing.net/data_ralay_country/api_for_third/get_car_wf.php'

    # 构造查询数据
    prefix = v_number[:1]  # 车牌前缀
    cph = v_number[1:]  # 车牌号
    name = 'third'
    key = hashlib.md5((cph + name + 'third123').encode()).hexdigest()

    data = {'prefix': prefix, 'cph': cph, 'cjh': v_code, 'fdj': e_code, 'cx': v_type, 'name': name, 'key': key}

    # url转码
    data = urllib.parse.urlencode(data)

    # 创建request请求
    request = urllib.request.Request(url, data.encode())

    try:
        # 获得response
        response = urllib.request.urlopen(request)
        response = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(e)
        response = {"state": 2, "msg": "查询异常"}
    return response


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

    # 创建request请求
    request = urllib.request.Request(url, headers=headers, data=data.encode('utf-8'))

    # 获得response
    response_data = urllib.request.urlopen(request)

    return json.loads(response_data.read().decode('utf-8'))


# 通过天津接口查询结果构造标准返回数据
def vio_dic_for_tj(data):
    if 'status' in data and data['status'] == 0:
        return data
    elif 'status' in data:
        return get_status(data['status'], 1)
    else:
        return {'status': 53, 'msg': '查询失败'}


# 通过典典接口查询结果构造标准返回数据
def vio_dic_for_ddyc(v_number, data):
    """
    通过典典接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 车轮接口返回数据, dict
    :return: 车八佰违章数据, dict
    """

    if 'success' in data and data['success']:
        status = 0

        vio_list = []
        if 'data' in data and 'violations' in data['data']:
            for vio in data['data']['violations']:
                # 缴费状态
                try:
                    if 'paymentStatus' in vio:
                        vio_pay = int(vio['paymentStatus'])
                    else:
                        vio_pay = -1
                except Exception as e:
                    print(e)
                    vio_pay = -1

                # 已经缴费的违章数据不再返回
                if vio_pay == 2:
                    continue

                # 违法时间
                if 'time' in vio:
                    vio_time = vio['time']
                else:
                    vio_time = ''

                # 违法地点
                if 'address' in vio:
                    vio_address = vio['address']
                else:
                    vio_address = ''

                # 违法行为
                if 'reason' in vio:
                    vio_activity = vio['reason']
                else:
                    vio_activity = ''

                # 扣分
                if 'point' in vio:
                    vio_point = str(vio['point'])
                else:
                    vio_point = ''

                # 罚款
                if 'fine' in vio:
                    vio_money = str(vio['fine'])
                else:
                    vio_money = ''

                # 违法代码
                if 'violationNum' in vio:
                    vio_code = vio['violationNum']
                else:
                    vio_code = ''

                # 处理机关
                if 'violationCity' in vio:
                    vio_loc = vio['violationCity']
                else:
                    vio_loc = ''

                # 处理状态
                try:
                    if 'processStatus' in vio:
                        vio_deal = int(vio['processStatus'])
                    else:
                        vio_deal = -1
                except Exception as e:
                    print(e)
                    vio_deal = -1

                if vio_deal == 3:
                    vio_deal = '1'
                elif vio_deal == -1:
                    vio_deal = '-1'
                else:
                    vio_deal = '0'

                if vio_pay == 2:
                    vio_pay = '1'
                elif vio_pay == -1:
                    vio_pay = '-1'
                else:
                    vio_pay = '0'

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
        if 'errCode' in data:
            return get_status(data['errCode'], 2)
        else:
            return {'status': 53, 'msg': '查询失败'}

    return vio_dict


# 通过车轮接口查询结果构造标准返回数据
def vio_dic_for_chelun(v_number, data):
    """
    通过车轮接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 车轮接口返回数据, dict
    :return: 车八佰违章数据, dict
    """
    if 'code' in data and data['code'] == 0 and 'data' in data and data['data'] is not None:
        status = 0

        vio_list = []

        for vio in data['data']:
            # 违法时间
            if 'date' in vio:
                vio_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(vio['date'])))
            else:
                vio_time = ''

            # 违法地点
            if 'address' in vio:
                vio_address = vio['address']
            else:
                vio_address = ''

            # 违法行为
            if 'detail' in vio:
                vio_activity = vio['detail']
            else:
                vio_activity = ''

            # 扣分
            if 'point' in vio:
                vio_point = str(vio['point'])
            else:
                vio_point = ''

            # 罚款
            if 'money' in vio:
                vio_money = str(vio['money'])
            else:
                vio_money = ''

            # 违法代码
            if 'code' in vio:
                vio_code = vio['code']
            else:
                vio_code = ''

            # 处理机关
            if 'office_name' in vio:
                vio_loc = vio['office_name']
            else:
                vio_loc = ''

            # 缴费状态
            vio_pay = '-1'

            # 处理状态
            vio_deal = '-1'

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
        if 'code' in data and 'msg' in data:
            return get_status(data['code'], 3, data['msg'])
        elif 'code' in data:
            return get_status(data['code'], 3)
        else:
            return {'status': 53, 'msg': '查询失败'}

    return vio_dict


# 通过盔甲接口查询结果构造标准返回数据
def vio_dic_for_kuijia(v_number, data):
    """
        通过盔甲接口查询结构构造标准返回数据
        :param v_number: 车牌
        :param data: 盔甲接口返回数据, dict
        :return: 车八佰违章数据, dict
        """
    if data.get('success', False):
        status = 0

        vio_list = []
        if 'data' in data and 'peccancy' in data['data'] and len(data['data']['peccancy']) > 0 and 'peccancies' in \
                data['data']['peccancy'][0]:
            for vio in data['data']['peccancy'][0]['peccancies']:
                # 缴费状态
                try:
                    if 'paystat' in vio:
                        vio_pay = int(vio['paystat'])
                    else:
                        vio_pay = -1
                except Exception as e:
                    print(e)
                    vio_pay = -1

                # 已经缴费的违章数据不再返回
                if vio_pay == 2:
                    continue

                # 处理状态
                try:
                    if 'status' in vio:
                        vio_deal = int(vio['status'])
                    else:
                        vio_deal = -1
                except Exception as e:
                    print(e)
                    vio_deal = -1

                if vio_deal == 3:
                    vio_deal = '1'
                elif vio_deal == -1:
                    vio_deal = '-1'
                else:
                    vio_deal = '0'

                if vio_pay == 2:
                    vio_pay = '1'
                elif vio_pay == -1:
                    vio_pay = '-1'
                else:
                    vio_pay = '0'

                # 违法时间
                if 'peccancyTime' in vio:
                    vio_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(vio['peccancyTime']) / 1000))
                else:
                    vio_time = ''

                # 违法地点
                if 'location' in vio:
                    vio_address = vio['location']
                else:
                    vio_address = ''

                # 违法行为
                if 'peccancyInfo' in vio:
                    vio_activity = vio['peccancyInfo']
                else:
                    vio_activity = ''

                # 扣分
                if 'point' in vio:
                    vio_point = str(vio['point'])
                else:
                    vio_point = ''

                # 罚款
                if 'fee' in vio:
                    vio_money = str(vio['fee'])
                else:
                    vio_money = ''

                # 违法代码
                if 'code' in vio:
                    vio_code = vio['code']
                else:
                    vio_code = ''

                # 处理机关
                if 'department' in vio:
                    vio_loc = vio['department']
                else:
                    vio_loc = ''

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
        if 'status' in data and 'message' in data:
            return get_status(data['status'], 4, data['message'])
        elif 'status' in data:
            return get_status(data['status'], 4)
        else:
            return {'status': 53, 'msg': '查询失败'}

    return vio_dict


# 通过zfb接口查询结果构造标准返回数据
def vio_dic_for_zfb(v_number, data):
    """
    通过车轮接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 车轮接口返回数据, dict
    :return: 车八佰违章数据, dict
    """
    if data.get('state') == 0:
        status = 0

        vio_list = []

        for vio in data.get('data'):
            # 违法时间
            vio_time = vio.get('wfsj', '')

            # 违法地点
            vio_address = vio.get('wfdz', '')

            # 违法行为
            vio_activity = vio.get('wfnr', '')

            # 扣分
            vio_point = str(vio.get('score', ''))

            # 罚款
            vio_money = str(vio.get('fkje', ''))

            # 违法代码
            vio_code = str(vio.get('wfxw', ''))

            # 处理机关
            vio_loc = ''

            # 缴费状态
            vio_pay = '-1'

            # 处理状态
            vio_deal = '-1'

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
        if 'state' in data and 'msg' in data:
            return get_status(data['code'], 3, data['msg'])
        else:
            return {'status': 53, 'msg': '查询失败'}

    return vio_dict


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


# 查询结果保存到本地数据库
def save_to_loc_db(vio_data, vehicle_number, vehicle_type):

    try:
        # 如果没有违章, 创建一条只包含车牌和车辆类型的数据
        if len(vio_data['data']) == 0:
            vio_info = VioInfo()
            vio_info.vehicle_number = vehicle_number
            vio_info.vehicle_type = vehicle_type
            vio_info.vio_code = '999999'                # 专用代码表示无违章

            vio_info.save()
        else:
            # 如果有, 逐条创建违章数据
            for vio in vio_data['data']:
                vio_info = VioInfo()
                vio_info.vehicle_number = vehicle_number
                vio_info.vehicle_type = vehicle_type
                vio_info.vio_time = vio['time']
                vio_info.vio_position = vio['position']
                vio_info.vio_activity = vio['activity']

                try:
                    vio_info.vio_point = int(vio['point'])
                except Exception as e:
                    print(e)

                try:
                    vio_info.vio_money = int(vio['money'])
                except Exception as e:
                    print(e)

                vio_info.vio_code = vio['code']
                vio_info.vio_loc = vio['location']
                vio_info.deal_status = int(vio['deal'])
                vio_info.pay_status = int(vio['pay'])

                vio_info.save()
    except Exception as e:
        print(e)

    # print('saved to local db')


# 保存查询日志
def save_log(v_number, origin_data, vio_data, user_id, url_id, user_ip, city=''):
    """
    保存典典返回的查询结果到日志
    :param v_number: 车牌号
    :param origin_data: 违章接口返回原始数据
    :param vio_data: 标准化后的违章数据
    :param user_id: 用户id
    :param url_id: 查询url_id
    :param user_ip: 用户ip
    :param city: 查询城市
    :return:
    """

    # 构造日志数据
    log_info = LogInfo()

    # 保存基本查询信息
    log_info.vehicle_number = v_number
    log_info.user_id = user_id
    log_info.url_id = url_id
    log_info.query_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_info.ip = user_ip
    log_info.city = city

    # 判断使用的接口url_id
    if url_id is None:

        log_info.status = 17
        log_info.msg = '查询城市错误'

    elif url_id == 99 or ('status' in vio_data and vio_data['status'] == 0):

        # 查询成功
        log_info.status = 0

    else:

        if 'status' in vio_data:
            log_info.status = vio_data['status']

        if 'msg' in vio_data:
            log_info.msg = vio_data['msg']

        if url_id == 1:

            # 天津接口
            if 'status' in origin_data:
                log_info.origin_status = origin_data['status']

            if 'msg' in origin_data:
                log_info.origin_msg = origin_data['msg']

        elif url_id == 2:

            # 典典接口
            if 'errCode' in origin_data:
                log_info.origin_status = origin_data['errCode']

            if 'message' in origin_data:
                log_info.origin_msg = origin_data['message']

        elif url_id == 3:

            # 车轮接口
            if 'code' in origin_data:
                log_info.origin_status = origin_data['code']

            if 'msg' in origin_data:
                log_info.origin_msg = origin_data['msg']

        elif url_id == 4:

            # 盔甲接口
            if 'status' in origin_data:
                log_info.origin_status = origin_data['status']

            if 'message' in origin_data:
                log_info.origin_msg = origin_data['message']

        elif url_id == 6:

            # 少帅接口
            log_info.origin_status = origin_data.get('error_code', '')
            log_info.origin_msg = origin_data.get('error_message', '')

    # 保存日志到数据库
    try:
        log_info.save()
    except Exception as e:
        print(e)


# 查询失败时保存日志
def save_error_log(status, msg, user_id, user_ip):
    """
    保存查询失败日志
    :param status: 返回状态码
    :param msg: 返回信息
    :param user_id: 用户id
    :param user_ip: 用户ip
    :return:
    """
    try:
        # 构造日志数据
        log_info = LogInfo()

        # 保存基本查询信息
        log_info.status = status
        log_info.msg = msg
        log_info.user_id = user_id
        log_info.ip = user_ip
        log_info.query_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 保存到数据库
        log_info.save()
    except Exception as e:
        print(e)


# 根据天津接口的返回状态码构造本地平台返回给用户的状态码
def create_status_from_tj(origin_status):

    if origin_status == 21:
        status = 31
        msg = '交管数据维护中'
    elif origin_status == 22:
        status = 32
        msg = '车牌号或车辆类型错误'
    elif origin_status == 23:
        status = 33
        msg = '发动机号错误'
    else:
        status = 51
        msg = '数据源异常'

    return {'status': status, 'msg': msg}


# 根据典典接口的返回状态码构造本地平台返回给用户的状态码
def create_status_from_ddyc(origin_status):
    if origin_status == 1015:
        status = 31
        msg = '交管数据维护中'
    elif origin_status in [1001, 1020, 1030]:
        status = 32
        msg = '车牌号或车辆类型错误'
    elif origin_status == 1021:
        status = 33
        msg = '发动机号错误'
    elif origin_status == 1022:
        status = 34
        msg = '车架号错误'
    elif origin_status == 1032:
        status = 35
        msg = '车架号或发动机号错误'
    elif origin_status == 1013:
        status = 39
        msg = '数据源不稳定, 请稍后再查'
    elif origin_status == 1031:
        status = 41
        msg = '该城市不支持查询'
    elif origin_status == 1016:
        status = 42
        msg = '该城市不支持外地车牌查询'
    elif origin_status == 1010:
        status = 43
        msg = '无权限查询'
    else:
        status = 51
        msg = '数据源异常'

    return {'status': status, 'msg': msg}


# 根据车轮接口的返回状态码构造本地平台返回给用户的状态码
def create_status_from_chelun(origin_status, origin_msg):

    if origin_status == -3:
        status = 31
        msg = '交管数据维护中'
    elif origin_status == -10 and origin_msg in['车辆类型参数错误', '车牌号码格式错误']:
        status = 32
        msg = '车牌号或车辆类型错误'
    elif origin_status == -10 and origin_msg == '请输入完整发动机号':
        status = 33
        msg = '发动机号错误'
    elif origin_status == -10 and origin_msg == '请输入完整车架号':
        status = 34
        msg = '车架号错误'
    elif origin_status == -2 and origin_msg == '输入信息有误，请核对':
        status = 36
        msg = '车辆信息不正确'
    elif origin_status == -2:
        status = 39
        msg = '数据源不稳定, 请稍后再查'
    elif origin_status == 0 and origin_msg == '接口升级中，开放时间待定':
        status = 39
        msg = '数据源不稳定, 请稍后再查'
    else:
        status = 51
        msg = '数据源异常'

    return {'status': status, 'msg': msg}


# 盔甲接口状态码
def create_status_from_kuijia(origin_status):

    if origin_status in [-1, -41, -6]:
        status = 36
        msg = '车辆信息不正确'
    elif origin_status == -3:
        status = 41
        msg = '该城市不支持查询'
    elif origin_status in [-5, -42]:
        status = 39
        msg = '数据源不稳定, 请稍后再查'
    elif origin_status in [-61, -66]:
        status = 32
        msg = '车牌号或车辆类型错误'
    elif origin_status == -62:
        status = 34
        msg = '车架号错误'
    elif origin_status == -63:
        status = 33
        msg = '发动机号错误'
    elif origin_status == -67:
        status = 42
        msg = '该城市不支持外地车牌查询'
    else:
        status = 51
        msg = '数据源异常'

    return {'status': status, 'msg': msg}


# zfb接口状态码
def create_status_from_zfb(origin_msg):

    if origin_msg == '发动机号错误':
        status = 33
        msg = '发动机号错误'
    elif origin_msg == '发动机号错误':
        status = 33
        msg = '发动机号长度不足6位！'
    else:
        status = 51
        msg = '数据源异常'

    return {'status': status, 'msg': msg}


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


# 根据不同接口的返回状态码构造本地平台返回给用户的状态码
def get_status(origin_status, url_id, origin_msg=''):

    # 天津接口
    if url_id == 1:
        return create_status_from_tj(int(origin_status))

    # 典典接口
    elif url_id == 2:
        return create_status_from_ddyc(int(origin_status))

    # 车轮接口
    elif url_id == 3:
        return create_status_from_chelun(int(origin_status), origin_msg)

    # 盔甲接口
    elif url_id == 4:
        return create_status_from_kuijia(int(origin_status))

    # zfb接口
    elif url_id == 5:
        return create_status_from_zfb(origin_msg)

    # 少帅接口
    elif url_id == 6:
        return create_status_from_shaoshuai(int(origin_status))

    else:
        return {'status': 52, 'msg': '违章查询接口异常'}


# 根据查询结果记录车辆信息
# 将车辆信息保存都本地数据库
# 判断本地数据库中是否已经存在该车辆信息, 如果已经存在, 判断车辆信息是否需要更新
def save_vehicle(v_number, v_type, v_code, e_code):
    try:
        vehicle_bakup = VehicleBackup.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)

        # 如果车辆已经存在
        if vehicle_bakup.exists():

            # 判断是否需要更新车辆信息
            if not vehicle_bakup.filter(vehicle_code=v_code).filter(engine_code=e_code).exists():
                vehicle_bakup.update(vehicle_code=v_code, engine_code=e_code,
                                     update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        # 如果不存在, 创建新的车辆信息, 并保存
        else:

            vehicle = VehicleBackup()
            vehicle.vehicle_number = v_number
            vehicle.vehicle_type = v_type
            vehicle.vehicle_code = v_code
            vehicle.engine_code = e_code

            vehicle.save()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    carno = '京HD9596'
    cartype = '02'
    vcode = 'LGBF5AE00HR276883'
    ecode = '751757V'
    car2 = {'v_number': '浙B78KG7', 'v_type': '02', 'v_code': 'LSVCJ2BM1HN043778', 'e_code': '415650'}
    response_data = get_vio_from_chelun(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])

    # response_data = get_vio_from_zfb(v_number=carno, v_type=cartype, v_code=vcode, e_code=ecode)

    # response_data = get_vio_from_tj('津N02070', '02')
    print(response_data)

    # v_data = vio_dic_for_ddyc(carno, response_data)
    # v_data = vio_dic_for_chelun(car2['v_number'], response_data)
    # print(v_data)
