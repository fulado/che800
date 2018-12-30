"""
神州租车查询接口
"""

import time
import base64
import json
import hashlib
import pymysql

from multiprocessing import Queue
from threading import Thread
from django.http import HttpResponse
from django.db import connection

from .models import UserInfo, VehicleInfoSz, VioInfoSz
from .utils import save_error_log, save_log, get_url_id, get_vio_from_loc, get_vio_from_tj, get_vio_from_ddyc, \
    get_vio_from_chelun, get_vio_from_kuijia, get_vio_from_zfb, vio_dic_for_tj, vio_dic_for_ddyc, vio_dic_for_chelun, \
    vio_dic_for_kuijia, vio_dic_for_zfb
from .views_old import save_log_old


# 用户登录
def login_service(request):

    # 判断当前时间, 每天02:00 ~ 02:20禁止查询, 系统自动日志
    current_hour = time.localtime().tm_hour
    current_min = time.localtime().tm_min

    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    if current_hour == 2 and current_min in range(0, 20):
        response_data = {'status': 19, 'message': '系统维护中, 请稍后访问'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(19, '系统维护中, 请稍后访问', '', user_ip)
        return HttpResponse(response_data)

    # 不接收get方式请求
    if request.method == 'GET':
        response_data = {'status': 14, 'message': '请求方式错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(14, '请求方式错误', '', user_ip)
        return HttpResponse(response_data)

    # 如果ip不在白名单返回状态码14, 暂不验证ip
    # if not IpInfo.objects.filter(ip_addr=user_ip).exists():
    #     result = {'status': 14}
    #     return JsonResponse(result)

    # 获取用户传递的参数
    param = request.POST.get('param', '')

    if param == '':
        response_data = {'status': 15, 'message': '无效请求'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(15, '无效请求', '', user_ip)
        return HttpResponse(response_data)

    param = json.loads(base64.b64decode(param).decode('utf-8').replace('\'', '\"'))

    try:
        # 获取用户名和密码
        username = param['username']
        password = param['password']

        # 对比用户和密码
        user = UserInfo.objects.filter(username=username).get(password=password)

        # 如果用户信息正确, 记录当前时间戳
        user.timestamp = int(time.time())

        user.save()
    except Exception as e:
        print(e)
        response_data = {'status': 1, 'message': '用户名或密码错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(1, '用户名或密码错误', '', user_ip)
        return HttpResponse(response_data)

    # 根据用户名密码和时间戳计算token
    token = '%s%d%s' % (username, user.timestamp, password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()

    # 构造返回数据
    response_data = base64.b64encode(json.dumps({'status': 9, 'token': token}).encode('utf-8'))
    save_error_log(9, 'login success', user.id, user_ip)
    return HttpResponse(response_data)


# 查询违章
def violation_service(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    # 获取用户传递的参数
    param = request.POST.get('param', '')

    if param == '':
        response_data = {'status': 15, 'message': '无效请求'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(15, '无效请求', '', user_ip)
        return HttpResponse(response_data)

    try:
        param = json.loads(base64.b64decode(param).decode('utf-8').replace('\'', '\"'))
    except Exception as e:
        print(e)
        response_data = {'status': 16, 'message': '请求参数错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(16, '请求参数错误', '', user_ip)
        return HttpResponse(response_data)

    # print(param)
    try:
        # 获取用户名和密码
        username = param['userId']
        user_token = param['token']

        # 对比用户和密码
        user = UserInfo.objects.get(username=username)
    except Exception as e:
        print(e)
        response_data = {'status': 11, 'message': '用户未登录'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(11, '用户未登录', '', user_ip)
        return HttpResponse(response_data)

    # 判断token是否过期
    current_timestamp = int(time.time())

    if current_timestamp - user.timestamp > 3600:
        response_data = {'status': 17, 'message': 'token已过期'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(17, 'token已过期', user.id, user_ip)
        return HttpResponse(response_data)

    # 计算token
    token = '%s%d%s' % (username, user.timestamp, user.password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()

    # 对比token
    if token != user_token:
        response_data = {'status': 18, 'message': 'token错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(18, 'token错误', user.id, user_ip)
        return HttpResponse(response_data)

    # 获取车辆数据
    try:
        v_data = param['cars'][0]
    except Exception as e:
        print(e)
        response_data = {'status': 21, 'message': '车辆信息不正确'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(21, '车辆信息不正确', user.id, user_ip)
        return HttpResponse(response_data)

    # 判断车辆类型
    try:
        v_type = int(v_data['carType'])
        if v_type < 10:
            v_type = '0%d' % v_type
        else:
            v_type = str(v_type)
    except Exception as e:
        print(e)
        response_data = {'status': 20, 'message': '车辆类型错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(20, '车辆类型错误', user.id, user_ip)
        return HttpResponse(response_data)

    # 判断车牌号
    try:
        v_number = v_data['platNumber']
        if v_type == '02' and len(v_number) < 7:
            raise Exception
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': '车牌号错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(5, '车牌号错误', user.id, user_ip)
        return HttpResponse(response_data)

    # 判断车辆识别代号, 发动机号
    try:
        vin = v_data['vinNumber']
        e_code = v_data['engineNumber']
    except Exception as e:
        print(e)
        response_data = {'status': 22, 'message': '车架号或发动机号错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(22, '车架号或发动机号错误', user.id, user_ip)
        return HttpResponse(response_data)

    if 'workcity' in v_data:
        city = v_data['workcity']
    else:
        city = ''

    response_data = get_violations_sz(v_number, v_type, vin, e_code, city, user.id, user_ip)
    # print(response_data)
    response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
    return HttpResponse(response_data)


# 根据车辆信息查询违章
def get_violations_sz(v_number, v_type, v_code='', e_code='', city='', user_id=99, user_ip='127.0.0.1'):
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

    # 先从车辆信息库中查询车辆违章查询状态，如果违章查询失败，直接返回失败原因

    # 查询违章
    vio_data = get_vio_from_loc_sz(v_number, v_type, user_ip)

    # 保存日志
    if 'status' in vio_data:
        save_log_old(v_number, '', vio_data, user_id, 90, user_ip)
    else:
        save_log_old(v_number, '', vio_data, user_id, 90, user_ip)

    return vio_data


# 从本地数据库查询违章
def get_vio_from_loc_sz(v_number, v_type, user_ip):
    # 从车辆信息库中查询车辆的状态，如果该车辆查询失败，直接返回失败信息
    try:
        vehicle_info = VehicleInfoSz.objects.filter(vehicle_number=v_number).get(vehicle_type=v_type)
        if vehicle_info.status != 0:
            return {'status': vehicle_info.status, 'message': vehicle_info.msg}
    except Exception as e:
        print(e)
        return {'status': '98', 'message': '车辆未注册'}

    try:
        vio_info_list = VioInfoSz.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)
    except Exception as e:
        print(e)
        return {'status': '99', 'message': '其它错误'}

    # 如果有数据, 构造违章信息
    if vio_info_list:
        vio_list = []
        for vio in vio_info_list:
            # 如果没有违章直接略过
            if vio.vio_code == '999999':
                continue

            if vio.deal_status == 1:
                deal_status = 3
            elif vio.deal_status == 0:
                deal_status = 1
            else:
                deal_status = -1

            if vio.pay_status == 1:
                pay_status = 2
            elif vio.pay_status == 0:
                pay_status = 1
            else:
                pay_status = -1

            vio_data = {
                'reason': vio.vio_activity if vio.vio_activity else '',
                'viocjjg': vio.vio_loc if vio.vio_loc else '',
                'punishPoint': str(vio.vio_point),
                'location': vio.vio_position if vio.vio_position else '',
                'time': vio.vio_time if vio.vio_time else '',
                'punishMoney': str(vio.vio_money),
                'paystat': str(pay_status),
                'state': str(deal_status),
                'viocode': vio.vio_code if vio.vio_code else ''
            }

            vio_list.append(vio_data)
        # print('%s -- local db' % v_number)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'updateTime': vehicle_info.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': '0'
        }

        vio_dict = {'feedback': feedback, 'result': result}

        return vio_dict
    else:
        return {'status': '97', 'message': '未查询到该车辆违章信息'}


# 车辆注册/注销服务
def register_service(request):

    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    # 获取用户传递的参数
    param = request.POST.get('param', '')

    if param == '':
        response_data = {'status': 15, 'message': '无效请求'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(15, '无效请求', '', user_ip)
        return HttpResponse(response_data)

    try:
        param = json.loads(base64.b64decode(param).decode('utf-8').replace('\'', '\"'))
    except Exception as e:
        print(e)
        response_data = {'status': 16, 'message': '请求参数错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(16, '请求参数错误', '', user_ip)
        return HttpResponse(response_data)

    # print(param)
    try:
        # 获取用户名和密码
        username = param['userId']
        user_token = param['token']

        # 对比用户和密码
        user = UserInfo.objects.get(username=username)
    except Exception as e:
        print(e)
        response_data = {'status': 11, 'message': '用户未登录'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(11, '用户未登录', '', user_ip)
        return HttpResponse(response_data)

    # 判断token是否过期
    current_timestamp = int(time.time())

    if current_timestamp - user.timestamp > 3600:
        response_data = {'status': 17, 'message': 'token已过期'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(17, 'token已过期', user.id, user_ip)
        return HttpResponse(response_data)

    # 计算token
    token = '%s%d%s' % (username, user.timestamp, user.password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()

    # 对比token
    if token != user_token:
        response_data = {'status': 18, 'message': 'token错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(18, 'token错误', user.id, user_ip)
        return HttpResponse(response_data)

    # 获取worktype, 注册 or 注销
    try:
        status = int(param['worktype'])
    except Exception as e:
        print(e)
        response_data = {'status': 30, 'message': 'worktype error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(30, 'worktype error', user.id, user_ip)
        return HttpResponse(response_data)

    # 获取车辆数据
    try:
        v_data = param['cars'][0]
    except Exception as e:
        print(e)
        response_data = {'status': 25, 'message': 'only one car register'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        save_error_log(25, 'only one car register', user.id, user_ip)
        return HttpResponse(response_data)

    # 判断车辆类型
    try:
        v_type = int(v_data['carType'])
        if v_type < 10:
            v_type = '0%d' % v_type
        else:
            v_type = str(v_type)
    except Exception as e:
        print(e)
        if status == 1:
            response_data = {'status': 22, 'message': 'register failure'}
            save_error_log(22, 'register failure', user.id, user_ip)
        else:
            response_data = {'status': 24, 'message': 'unregister failure'}
            save_error_log(24, 'unregister failure', user.id, user_ip)

        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断车牌号
    try:
        v_number = v_data['platNumber']
        if v_type == '02' and len(v_number) < 7:
            raise Exception
    except Exception as e:
        print(e)
        if status == 1:
            response_data = {'status': 22, 'message': 'register failure'}
            save_error_log(22, 'register failure', user.id, user_ip)
        else:
            response_data = {'status': 24, 'message': 'unregister failure'}
            save_error_log(24, 'unregister failure', user.id, user_ip)

        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断车辆识别代号, 发动机号
    try:
        vin = v_data['vinNumber']
        e_code = v_data['engineNumber']
    except Exception as e:
        print(e)
        if status == 1:
            response_data = {'status': 22, 'message': 'register failure'}
            save_error_log(22, 'register failure', user.id, user_ip)
        else:
            response_data = {'status': 24, 'message': 'unregister failure'}
            save_error_log(24, 'unregister failure', user.id, user_ip)

        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 获取运营城市
    city = v_data.get('city', '')

    response_data = vehicle_register(v_number, v_type, vin, e_code, status, city, user.id)

    # 保存车辆注册/注销日志
    save_log_old(v_number, '', response_data, user.id, 98, user_ip)

    response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
    return HttpResponse(response_data)


# 车辆注册/注销
def vehicle_register(v_number, v_type, v_code, e_code, status, city, user_id):
    """
    接受用户发送的车辆信息, 根据status选择注册或注销, 1-注册, 2-注销
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :param status: 注册/注销
    :param city: 运营城市
    :param user_id: 用户id
    :return: 注册是否成功, json格式
    """
    if status not in [1, 2]:
        return {'status': 30, 'message': 'worktype error'}

    # 注销
    if status == 2:
        try:
            vehicle_set = VehicleInfoSz.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)

            if vehicle_set.exists():
                vehicle_set.delete()
                return {'status': 23, 'message': 'unregister success'}
            else:
                return {'status': 28, 'message': 'The car is not registered'}
        except Exception as e:
            print(e)
            return {'status': 24, 'message': 'unregister failure'}

    # 注册
    # 将v_type转为int型
    v_type = int(v_type)

    try:
        # 在数据库中检索车辆信息
        vehicle_set = VehicleInfoSz.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)

        # 如果车辆已经存在, 更新车辆信息
        if vehicle_set.exists():
            if not vehicle_set.filter(vehicle_code=v_code).filter(engine_code=e_code).exists():
                vehicle_set.update(vehicle_code=v_code, engine_code=e_code, city=city,
                                   update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

                return {'status': 21, 'message': 'register success'}
            else:
                return {'status': 27, 'message': 'The car has registered'}
        # 如果车辆不存在, 保存新的车辆数据
        else:
            vehicle_info = VehicleInfoSz()

            vehicle_info.vehicle_number = v_number
            vehicle_info.vehicle_type = v_type
            vehicle_info.vehicle_code = v_code
            vehicle_info.engine_code = e_code
            vehicle_info.city = city
            vehicle_info.user_id = user_id
            vehicle_info.msg = '车辆未查询'

            vehicle_info.save()

            return {'status': 21, 'message': 'register success'}
    except Exception as e:
        print(e)
        return {'status': 22, 'message': 'register failure'}


# 根据车辆信息查询违章
def get_violations(v_number, v_type=2, v_code='', e_code='', city='', user_id=99, user_ip='127.0.0.1'):
    """
    根据车辆信息调用不同的接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :param city: 查询城市
    :param user_id: 用户id
    :param user_ip: 用户ip
    :return: 违章数据, json格式
    """

    # 将车辆类型转为int型
    v_type = int(v_type)

    # 先从本地数据库查询, 如果本地数据库没有该违章数据, 再通过接口查询
    vio_data = get_vio_from_loc(v_number, v_type)

    # 如果查询成功, 保存日志, 并返回查询结果
    if vio_data is not None:

        # 保存日志
        save_log(v_number, '', '', user_id, 99, user_ip, city)

        return vio_data

    # 将车牌类型转为字符串'02'
    if v_type < 10:
        v_type = '0%d' % v_type
    else:
        v_type = str(v_type)

    # 根据城市选择确定查询端口的url_id
    url_id, city = get_url_id(v_number, city)

    # 如果url_id是None就返回查询城市错误
    if url_id is None:
        save_log(v_number, '', '', user_id, url_id, user_ip, city)
        return {'status': 17, 'msg': '查询城市错误'}  # 查询城市错误

    # 根据url_id调用不同接口, 1-天津接口, 2-典典接口, 3-车轮接口
    if url_id == 1:
        # 从天津接口查询违章数据
        origin_data = get_vio_from_tj(v_number, v_type, e_code)

        # 将接口返回的原始数据标准化
        vio_data = vio_dic_for_tj(origin_data)
    elif url_id == 2:
        origin_data = get_vio_from_ddyc(v_number, v_type, v_code, e_code, city)
        vio_data = vio_dic_for_ddyc(v_number, origin_data)
    elif url_id == 3:
        # 从车轮接口查询违章数据, 并标准化
        origin_data = get_vio_from_chelun(v_number, v_type, v_code, e_code)
        vio_data = vio_dic_for_chelun(v_number, origin_data)
    elif url_id == 4:
        # 从盔甲接口查询违章数据
        origin_data = get_vio_from_kuijia(v_number, v_code, e_code)
        vio_data = vio_dic_for_kuijia(v_number, origin_data)
    elif url_id == 5:
        # 从zfb接口查询违章数据
        origin_data = get_vio_from_zfb(v_number, v_code, e_code)
        vio_data = vio_dic_for_zfb(v_number, origin_data)
    else:
        # 返回该地区不支持查询
        origin_data = ''
        vio_data = {'status': 41, 'msg': '该城市不支持查询'}

    # 保存日志
    save_log(v_number, origin_data, vio_data, user_id, url_id, user_ip, city)

    # 如果查询成功
    if vio_data['status'] == 0:

        # 保存违章数据到本地数据库
        save_to_loc_db(vio_data, v_number, int(v_type))

    # 不能直接返回data, 应该把data再次封装后再返回
    return vio_data


# 查询结果保存到本地数据库
def save_to_loc_db(vio_data, vehicle_number, vehicle_type):

    try:
        # 如果没有违章, 创建一条只包含车牌和车辆类型的数据
        if len(vio_data['data']) == 0:
            vio_info = VioInfoSz()
            vio_info.vehicle_number = vehicle_number
            vio_info.vehicle_type = vehicle_type
            vio_info.vio_code = '999999'                # 专用代码表示无违章

            vio_info.save()
        else:
            # 如果有, 逐条创建违章数据
            for vio in vio_data['data']:
                vio_info = VioInfoSz()
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


# 车辆读取线程
def get_vehicle_thread(v_queue):

    # 循环3次, 每次只查询之前查询失败的车辆
    for i in range(3):
        # 查询数据库中的车辆数据, 已经查询成功的不再查询
        try:
            connection.connection.ping()
        except:
            connection.close()
        finally:
            vehicle_list = VehicleInfoSz.objects.exclude(status__in=[0, 32, 33, 34, 35, 36, 41, 42]).\
                exclude(vehicle_number__contains='浙')

        # 查询违章
        for vehicle in vehicle_list:
            # 将车辆信息放入队列
            v_queue.put(vehicle, True)

        time.sleep(600)

    for i in range(3):
        try:
            connection.connection.ping()
        except:
            connection.close()
        finally:
            vehicle_list = VehicleInfoSz.objects.exclude(status__in=[0, 32, 33, 34, 35, 36, 41, 42]).\
                filter(vehicle_number__contains='浙')

        for vehicle in vehicle_list:
            # 将车辆信息放入队列
            v_queue.put(vehicle, True)

        time.sleep(600)


# 违章查询线程
def query_thread(v_queue):
    while True:
        try:
            # print('query thread %d start' % t_id)
            vehicle = v_queue.get(True, 5)
            # print(vehicle.vehicle_number)
            data = get_violations(vehicle.vehicle_number, vehicle.vehicle_type, vehicle.vehicle_code,
                                  vehicle.engine_code, vehicle.city)

            # 如果查询成功, 将车辆查询状态置为1
            vehicle.status = data.get('status', 99)
            vehicle.msg = data.get('message', '')
            vehicle.save()
        except Exception as e:
            print(e)
            break


# 定时任务, 查询车辆库中车辆违章数据
def query_vio_auto_sz():
    # 创建车辆队列
    vehicle_queue = Queue(5)

    # 创建车辆读取线程
    t_get_vehicle_thread = Thread(target=get_vehicle_thread, args=(vehicle_queue,))
    t_get_vehicle_thread.start()

    # 创建5个车辆查询线程
    for i in range(5):
        t_query_thread = Thread(target=query_thread, args=(vehicle_queue,))
        t_query_thread.start()


# 定时任务, 备份并初始化违章表和日志表
def backup_vio():

    # 数据库连接信息
    # host = 'bj-cdb-gq8xi5ya.sql.tencentcdb.com'
    # port = 63226
    host = '172.21.0.2'
    port = 3306
    password = 'Init1234'
    user = 'root'
    database = 'violation'
    charset = 'utf8mb4'

    try:
        # 创建连接
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

        # 获取Cursor对象
        cs = conn.cursor()

        # 计算昨天的时间
        yesterday_time = time.time() - 60 * 60 * 12
        # 表名中包含的日期
        name_time = time.strftime('%Y%m%d', time.localtime(yesterday_time))

        # 违章表改名
        sql = 'RENAME TABLE vio_sch_vioinfosz TO vio_sch_vioinfosz_%s;' % name_time
        cs.execute(sql)

        # 新建违章表
        sql = """CREATE TABLE `vio_sch_vioinfosz` (
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
                    `deal_status` int(11),
                    `pay_status` int(11),
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        cs.execute(sql)
    except Exception as e:
        print(e)

    finally:
        # 关闭Cursor
        cs.close()

        # 关闭连接
        conn.close()


# 重置车辆状态
def reset_vehicle():
    # 判断连接是否可用, 如不可用关闭连接
    try:
        connection.connection.ping()
    except:
        connection.close()
    finally:
        VehicleInfoSz.objects.all().update(status=99, spider_status=False, msg='车辆未查询')
