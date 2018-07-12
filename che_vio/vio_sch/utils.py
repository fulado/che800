import time
import hashlib
import json
import urllib.request
from .models import VioInfo, LogInfo, LocInfo


# 判断查询城市是否正确
def get_url_id(v_number, city):
    if city not in ['天津市', '天津', '津']:
        city = ''  # 未来如有需要在修改次功能

    try:
        if city != '':
            loc_info = LocInfo.objects.get(loc_name__contains=city)
        else:
            plate_name = v_number[0]
            loc_info = LocInfo.objects.get(plate_name=plate_name)
    except Exception as e:
        print(e)
        return None
    else:
        # city = loc_info.loc_name
        url_id = loc_info.url_id.id

    return url_id


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
                'time': vio.vio_time,
                'position': vio.vio_position,
                'activity': vio.vio_activity,
                'point': vio.vio_point,
                'money': vio.vio_money,
                'code': vio.vio_code,
                'location': vio.vio_loc
            }

            vio_list.append(vio_data)
        # print('%s -- local db' % v_number)

        return {'vehicleNumber': v_number, 'status': 0, 'data': vio_list}
    else:
        return None


# 从天津接口查询违章数据
def get_vio_from_tj(v_number, v_type):
    """
    从天津接口查询违章数据
    :param v_number: 车牌号
    :param v_type: 车辆类型
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
            'vehicleType': v_type}

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
                if 'paymentStatus' in vio:
                    vio_pay = int(vio['paymentStatus'])
                else:
                    vio_pay = 1

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
                    vio_point = vio['point']
                else:
                    vio_point = ''

                # 罚款
                if 'fine' in vio:
                    vio_money = vio['fine']
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

                vio_data = {
                    'time': vio_time,
                    'position': vio_address,
                    'activity': vio_activity,
                    'point': vio_point,
                    'money': vio_money,
                    'code': vio_code,
                    'location': vio_loc
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
    if 'code' in data and data['code'] == 0:
        status = 0

        vio_list = []
        if 'data' in data:
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
                    vio_point = vio['point']
                else:
                    vio_point = ''

                # 罚款
                if 'money' in vio:
                    vio_money = vio['money']
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

                vio_data = {
                    'time': vio_time,
                    'position': vio_address,
                    'activity': vio_activity,
                    'point': vio_point,
                    'money': vio_money,
                    'code': vio_code,
                    'location': vio_loc
                }

                vio_list.append(vio_data)

        vio_dict = {'vehicleNumber': v_number, 'status': status, 'data': vio_list}
    else:
        vio_dict = {'vehicleNumber': v_number, 'status': 21}  # 查询失败

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
                vio_info.vio_point = vio['point']
                vio_info.vio_money = vio['money']
                vio_info.vio_code = vio['code']
                vio_info.vio_loc = vio['location']

                vio_info.save()
    except Exception as e:
        print(e)

    # print('saved to local db')


# 保存查询日志
def save_log(v_number, vio_data, user_id, url_id, user_ip):
    """
    保存典典返回的查询结果到日志
    :param v_number:
    :param vio_data:
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

    # 判断使用的接口url_id
    if url_id == 1:

        # 天津接口
        if 'status' in vio_data and vio_data['status'] == 0:
            # 查询成功
            log_info.status = 0
            log_info.comments = '查询成功'
        else:
            # 查询失败
            if 'status' in vio_data:
                log_info.status = vio_data['status']
            log_info.comments = '查询失败'

    elif url_id == 2:

        # 典典接口
        if 'success' in vio_data and vio_data['success']:
            # 如果查询成功, 保存查询成功
            log_info.status = 0
            log_info.comments = '查询成功'
        else:
            # 如果查询失败, 保存错误代码和错误信息
            if 'errCode' in vio_data:
                log_info.status = vio_data['errCode']

            if 'message' in vio_data:
                log_info.comments = vio_data['message']

    elif url_id == 3:

        # 车轮接口
        if 'code' in vio_data and vio_data['code'] == 0:
            # 查询成功
            log_info.status = 0
            log_info.comments = '查询成功'
        else:
            # 查询失败
            if 'code' in vio_data:
                log_info.status = vio_data['code']

            if 'msg' in vio_data:
                log_info.comments = vio_data['msg']

    elif url_id is None:

        log_info.status = 16
        log_info.comments = '查询城市错误'

    else:

        # 本地数据库
        log_info.status = 0
        log_info.comments = '查询成功'

    # 保存日志到数据库
    try:
        log_info.save()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    carno = '京HD9596'
    cartype = '02'
    vcode = 'LGBF5AE00HR276883'
    ecode = '751757V'
    car2 = {'v_number': '沪AUT71', 'v_type': '02', 'v_code': 'LSKG4AC12FA411099', 'e_code': 'H1SF1220128'}
    # response_data = get_vio_from_chelun(car2['v_number'], car2['v_type'], car2['v_code'], car2['e_code'])

    # response_data = get_vio_from_ddyc(v_number=carno, v_type=cartype, v_code=vcode, e_code=ecode, city='杭州市')

    # response_data = get_vio_from_tj('津N02070', '02')
    # print(response_data)

    # v_data = vio_dic_for_ddyc(carno, response_data)
    # v_data = vio_dic_for_chelun(car2['v_number'], response_data)
    # print(v_data)
