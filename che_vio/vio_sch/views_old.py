"""
老接口应用
"""
from django.http import JsonResponse, HttpResponse
from .models import UserInfo, VioInfo
from .utils import get_vio_from_tj, get_vio_from_ddyc, get_vio_from_chelun, get_url_id, save_log
import base64
import json
import time
import hashlib


# 用户登录
def login_service(request):
    # 不接收get方式请求
    if request.method == 'GET':
        response_data = {'status': 31, 'message': 'request method error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断请求ip是否在白名单中
    # if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
    #     user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    # else:
    #     user_ip = request.META['REMOTE_ADDR']

    # 如果ip不在白名单返回状态码14, 暂不验证ip
    # if not IpInfo.objects.filter(ip_addr=user_ip).exists():
    #     result = {'status': 14}
    #     return JsonResponse(result)

    # 获取用户传递的参数
    param = request.POST.get('param', '')
    print(param)
    if param == '':
        response_data = {'status': 99, 'message': 'request invalid'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    param = json.loads(base64.b64decode(param).decode('utf-8').replace('\'', '\"'))

    try:
        # 获取用户名和密码
        username = param['username']
        password = param['password']
        print('%s : %s' % (username, password))

        # 对比用户和密码
        user = UserInfo.objects.filter(username=username).get(password=password)

        # 如果用户信息正确, 记录当前时间戳
        user.timestamp = int(time.time())
        user.save()
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'username or password error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 根据用户名密码和时间戳计算token
    token = '%s%d%s' % (username, user.timestamp, password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()

    # 构造返回数据
    response_data = base64.b64encode(json.dumps({'status': 0, 'token': token}).encode('utf-8'))

    return HttpResponse(response_data)


# 查询违章
def violation_service(request):
    # 获取用户传递的参数
    param = request.POST.get('param', '')

    if param == '':
        response_data = {'status': 99, 'message': 'request invalid'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断请求ip是否在白名单中
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    param = json.loads(base64.b64decode(param).decode('utf-8').replace('\'', '\"'))

    try:
        # 获取用户名和密码
        username = param['userId']
        user_token = param['token']

        # 对比用户和密码
        user = UserInfo.objects.get(username=username)
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'userId or token error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断token是否过期
    current_timestamp = int(time.time())
    if current_timestamp - user.timestamp > 3600:
        response_data = {'status': 5, 'message': 'token is out of time'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 计算token
    token = '%s%d%s' % (username, user.timestamp, user.password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()

    # 对比token
    if token != user_token:
        response_data = {'status': 5, 'message': 'userId or token error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断车辆类型
    try:
        v_type = int(param['vehicleType'])
        if v_type < 10:
            v_type = '0%d' % v_type
        else:
            v_type = str(v_type)
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'vehicle type error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断车牌号
    try:
        v_number = param['platNumber']
        if v_type == '02' and len(v_number) < 7:
            raise Exception
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'vehicle platNumber error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断车辆识别代号, 发动机号
    try:
        vin = param['vinNumber']
        e_code = param['engineNumber']
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'vin or engine code error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    if 'city' in param:
        city = param['workcity']
    else:
        city = ''

    get_violations_old(v_number, v_type, vin, e_code, city, user.id, user_ip)


# 根据车辆信息查询违章
def get_violations_old(v_number, v_type=2, v_code='', e_code='', city='', user_id=99, user_ip='127.0.0.1'):
    """
    根据车辆信息调用不同的接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :param city: 查询城市
    :param user_id: 用户id
    :param user_ip: 查询ip地址
    :return: 违章数据, json格式
    """
    # 将车辆类型转为int型
    v_type = int(v_type)

    # 先从本地数据库查询, 如果本地数据库没有该违章数据, 再通过接口查询
    result = get_vio_from_loc_old(v_number, v_type, user_ip)

    # 如果查询成功, 保存日志, 并返回查询结果
    if result is not None:

        # 保存日志
        save_log(v_number, '', user_id, 99, user_ip)

        return result

    # 获取查询城市和查询url_id
    # 目前看来这个功能没啥用, 暂时先把它省略了吧, 只判断车牌开头的城市简称, 根据这个确定调用哪个查询接口, 现在只查询天津的车
    # 将车牌类型转为字符串'02'
    if v_type < 10:
        v_type = '0%d' % v_type
    else:
        v_type = str(v_type)

    # 根据城市选择确定查询端口的url_id
    url_id = get_url_id(v_number, city)

    # 如果url_id是None就返回查询城市错误
    if url_id is None:
        save_log(v_number, '', user_id, 99, user_ip)
        return {'status': 16}  # 查询城市错误

    # 根据url_id调用不同接口, 1-天津接口, 2-典典接口, 3-车轮接口
    if url_id == 1:

        data = get_vio_from_tj(v_number, v_type)
        # print('%s -- tj api' % v_number)

        # 保存日志
        save_log(v_number, data, user_id, url_id, user_ip)

    elif url_id == 2:

        data = get_vio_from_ddyc(v_number, v_type, v_code, e_code, city)
        # print(data)
        # 保存日志
        save_log(v_number, data, user_id, url_id, user_ip)
        data = vio_div_for_ddyc_old(v_number, data, user_ip)
        # print('%s -- ddyc api' % v_number)

    else:

        data = get_vio_from_chelun(v_number, v_type, v_code, e_code)
        # print(data)
        # 保存日志
        save_log(v_number, data, user_id, url_id, user_ip)
        data = vio_dic_for_chelun_old(v_number, data, user_ip)

        # print('%s -- chelun api' % v_number)
    # print(data['status'])

    # 如果查询成功, 保存数据到本地数据库
    if data['status'] == 0:
        save_to_loc_db_old(data, v_number, int(v_type))

    # 不能直接返回data, 应该把data再次封装后再返回
    return data


# 从本地数据库查询违章
def get_vio_from_loc_old(v_number, v_type, user_ip):
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
                'reason': vio.vio_activity,
                'viocjjg': vio.vio_loc,
                'punishPoint': vio.vio_point,
                'location': vio.vio_position,
                'time': vio.vio_time,
                'punishMoney': vio.vio_money,
                'paystat': None,
                'state': None
            }

            vio_list.append(vio_data)
        # print('%s -- local db' % v_number)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list
        }

        vio_dict = {'feedback': feedback, 'result': result}

        return vio_dict
    else:
        return None


# 根据典典返回数据构造违章数据
def vio_div_for_ddyc_old(v_number, data, user_ip):
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
                    'reason': vio_activity,
                    'viocjjg': vio_loc,
                    'punishPoint': vio_point,
                    'location': vio_address,
                    'time': vio_time,
                    'punishMoney': vio_money,
                    'paystat': None,
                    'state': None
                }

                vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败
        if 'errCode' in data:
            status = data['errCode']

        if 'message' in data:
            message = data['message']

        vio_dict = {'status': status, 'message': message}

    return vio_dict


# 根据车轮返回数据构造违章数据
def vio_dic_for_chelun_old(v_number, data, user_ip):

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
                    'reason': vio_activity,
                    'viocjjg': vio_loc,
                    'punishPoint': vio_point,
                    'location': vio_address,
                    'time': vio_time,
                    'punishMoney': vio_money,
                    'paystat': None,
                    'state': None
                }

                vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败
        if 'code' in data:
            status = data['code']

        if 'msg' in data:
            message = data['msg']

        vio_dict = {'status': status, 'message': message}

    return vio_dict


# 查询结果保存到本地数据库
def save_to_loc_db_old(vio_data, vehicle_number, vehicle_type):

    try:
        # 如果没有违章, 创建一条只包含车牌和车辆类型的数据
        if len(vio_data['result']['punishs']) == 0:
            vio_info = VioInfo()
            vio_info.vehicle_number = vehicle_number
            vio_info.vehicle_type = vehicle_type
            vio_info.vio_code = '999999'                # 专用代码表示无违章

            vio_info.save()
        else:
            # 如果有, 逐条创建违章数据
            for vio in vio_data['result']['punishs']:
                vio_info = VioInfo()
                vio_info.vehicle_number = vehicle_number
                vio_info.vehicle_type = vehicle_type
                vio_info.vio_time = vio['time']
                vio_info.vio_position = vio['location']
                vio_info.vio_activity = vio['reason']
                vio_info.vio_point = vio['punishPoint']
                vio_info.vio_money = vio['punishMoney']
                vio_info.vio_loc = vio['viocjjg']

                vio_info.save()
    except Exception as e:
        print(e)


