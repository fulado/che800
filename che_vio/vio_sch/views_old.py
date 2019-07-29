"""
老接口应用
"""
from django.http import HttpResponse
from .models import UserInfo, VioInfo, LogInfo, VehicleInfo
from .utils import get_vio_from_tj, get_vio_from_ddyc, get_vio_from_chelun, get_url_id, save_error_log, save_vehicle, \
    get_vio_from_kuijia, get_vio_from_zfb, get_vio_from_shaoshuai, get_vio_from_doyun, get_vio_from_cwb, \
    get_loc_by_vio_id
import base64
import json
import time
import hashlib


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

    response_data = get_violations_old(v_number, v_type, vin, e_code, city, user.id, user_ip)
    # print(response_data)
    response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
    return HttpResponse(response_data)


# 根据车辆信息查询违章
def get_violations_old(v_number, v_type, v_code='', e_code='', city='', user_id=99, user_ip='127.0.0.1'):
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
    vio_data = get_vio_from_loc_old(v_number, v_type, user_ip)

    # 如果查询成功, 保存日志, 并返回查询结果
    if vio_data is not None:

        # 保存日志
        save_log_old(v_number, '', '', user_id, 99, user_ip, city)

        return vio_data

    # 获取查询城市和查询url_id
    # 目前看来这个功能没啥用, 暂时先把它省略了吧, 只判断车牌开头的城市简称, 根据这个确定调用哪个查询接口, 现在只查询天津的车
    # 将车牌类型转为字符串'02'
    if v_type < 10:
        v_type = '0%d' % v_type
    else:
        v_type = str(v_type)

    # 根据城市选择确定查询端口的url_id
    url_id, city = get_url_id(v_number, city)

    # 如果url_id是None就返回查询城市错误
    if url_id is None:
        save_log_old(v_number, '', '', user_id, url_id, user_ip, city)
        return {'status': 23, 'message': '查询城市错误'}  # 查询城市错误

    # 根据url_id调用不同接口, 1-天津接口, 2-典典接口, 3-车轮接口
    if url_id == 1:

        origin_data = get_vio_from_tj(v_number, v_type, e_code)
        vio_data = vio_dic_for_tj_old(v_number, origin_data, user_ip)
    elif url_id == 2:
        # 从典典接口查询违章数据, 并标准化
        origin_data = get_vio_from_ddyc(v_number, v_type, v_code, e_code, city)
        vio_data = vio_dic_for_ddyc_old(v_number, origin_data, user_ip)
    elif url_id == 3:
        # 从车轮接口查询违章数据, 并标准化
        # origin_data = get_vio_from_chelun(v_number, v_type, v_code, e_code)
        # vio_data = vio_dic_for_chelun_old(v_number, origin_data, user_ip)
        # 返回该地区不支持查询
        origin_data = ''
        vio_data = {'status': 51, 'message': '数据源异常'}  # 因为浙江接口查询很慢，为了防止浙江数据造成神州一直查不完
    elif url_id == 4:
        # 从盔甲接口查询违章数据
        origin_data = get_vio_from_kuijia(v_number, v_code, e_code)
        vio_data = vio_dic_for_kuijia_old(v_number, origin_data, user_ip)
    elif url_id == 5:
        # 从zfb接口查询违章数据
        origin_data = get_vio_from_zfb(v_number, v_type, v_code, e_code)
        vio_data = vio_dic_for_zfb_old(v_number, origin_data, user_ip)
    elif url_id == 6:
        # 从少帅接口查询违章数据
        origin_data = get_vio_from_shaoshuai(v_number, v_type, v_code, e_code)
        vio_data = vio_dic_for_shaoshuai_old(v_number, origin_data, user_ip)
    elif url_id == 7:
        # 从懂云接口查询违章数据, 并标准化
        origin_data = get_vio_from_doyun(v_number, v_type, v_code, e_code, city)
        vio_data = vio_dic_for_ddyc_old(v_number, origin_data, user_ip)
    elif url_id == 8:
        # 从车务帮接口查询违章数据, 并标准化
        origin_data = get_vio_from_cwb(v_number, v_type, v_code, e_code, city)
        vio_data = vio_dic_for_cwb_old(v_number, origin_data, user_ip)
    else:
        # 返回该地区不支持查询
        origin_data = ''
        vio_data = {'status': 41, 'message': '该城市不支持查询'}

    # 保存日志
    save_log_old(v_number, origin_data, vio_data, user_id, url_id, user_ip, city)

    # 如果查询成功, 保存数据到本地数据库
    if 'result' in vio_data:

        # 保存违章数据到本地数据库
        save_to_loc_db_old(vio_data, v_number, int(v_type))

        # 保存车辆数据到本地数据库
        save_vehicle(v_number, v_type, v_code, e_code)

    # 不能直接返回data, 应该把data再次封装后再返回
    return vio_data


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
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': '0'
        }

        vio_dict = {'feedback': feedback, 'result': result}

        return vio_dict
    else:
        return None


# 根据典典返回数据构造违章数据
def vio_dic_for_ddyc_old(v_number, data, user_ip):
    if 'success' in data and data['success']:
        status = '0'

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
                    vio_point = vio['point']
                else:
                    vio_point = ''

                # 罚款
                if 'fine' in vio:
                    vio_money = vio['fine']
                else:
                    vio_money = ''

                # 处理机关
                if 'violationCity' in vio:
                    vio_loc = vio['violationCity']
                else:
                    vio_loc = ''

                # 违法代码
                if 'violationNum' in vio:
                    vio_code = vio['violationNum']
                else:
                    vio_code = ''

                # 违法处理状态
                try:
                    if 'processStatus' in vio:
                        vio_status = vio['processStatus']
                    else:
                        vio_status = -1
                except Exception as e:
                    print(e)
                    vio_status = -1

                vio_data = {
                    'reason': vio_activity,
                    'viocjjg': vio_loc,
                    'punishPoint': str(vio_point),
                    'location': str(vio_address),
                    'time': vio_time,
                    'punishMoney': vio_money,
                    'paystat': str(vio_pay),
                    'state': str(vio_status),
                    'viocode': vio_code
                }

                vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': status
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败
        if 'errCode' in data:
            origin_status = data['errCode']

            if origin_status == 1015:
                status = 31
                message = '交管数据维护中'
            elif origin_status in [1001, 1020, 1030]:
                status = 5
                message = '车牌号错误'
            elif origin_status == 1021:
                status = 6
                message = '发动机号错误'
            elif origin_status == 1022:
                status = 7
                message = '车架号错误'
            elif origin_status == 1032:
                status = 8
                message = '车架号或发动机号错误'
            elif origin_status == 1013:
                status = 39
                message = '数据源不稳定, 请稍后再查'
            elif origin_status == 1031:
                status = 41
                message = '该城市不支持查询'
            elif origin_status == 1016:
                status = 42
                message = '该城市不支持外地车牌查询'
            elif origin_status == 1010:
                status = 43
                message = '无权限查询'
            else:
                status = 51
                message = '数据源异常'
        else:
            status = 99
            message = '其它错误'

        vio_dict = {'status': status, 'message': message}

    return vio_dict


# 根据车轮返回数据构造违章数据
def vio_dic_for_chelun_old(v_number, data, user_ip):

    if 'code' in data and data['code'] == 0:
        status = '0'

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

                # 处理机关
                if 'office_name' in vio:
                    vio_loc = vio['office_name']
                else:
                    vio_loc = ''

                # 违法代码
                if 'code' in vio:
                    vio_code = vio['code']
                else:
                    vio_code = ''

                vio_data = {
                    'reason': vio_activity,
                    'viocjjg': vio_loc,
                    'punishPoint': vio_point,
                    'location': vio_address,
                    'time': vio_time,
                    'punishMoney': vio_money,
                    'paystat': '-1',
                    'state': '-1',
                    'viocode': vio_code
                }

                vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': status
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败
        if 'code' in data:
            status = data['code']
        else:
            status = 99

        if 'msg' in data:
            message = data['msg']
        else:
            message = 'query error'

        vio_dict = {'status': status, 'message': message}

    return vio_dict


# 根据天津接口返回数据构造违章数据
def vio_dic_for_tj_old(v_number, data, user_ip):

    if 'status' in data and data['status'] == 0:
        status = '0'

        vio_list = []
        if 'data' in data:
            for vio in data['data']:
                # 违法时间
                if 'time' in vio:
                    vio_time = vio['time']
                else:
                    vio_time = ''

                # 违法地点
                if 'position' in vio:
                    vio_address = vio['position']
                else:
                    vio_address = ''

                # 违法行为
                if 'activity' in vio:
                    vio_activity = vio['activity']
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

                # 处理机关
                if 'location' in vio:
                    vio_loc = vio['location']
                else:
                    vio_loc = ''

                # 违法代码
                if 'code' in vio:
                    vio_code = vio['code']
                else:
                    vio_code = ''

                # 违法处理状态
                if 'deal' in vio:
                    vio_status = int(vio['deal'])
                else:
                    vio_status = -1

                if vio_status == 0:
                    vio_status = 1
                elif vio_status == 1:
                    vio_status = 3

                vio_data = {
                    'reason': vio_activity,
                    'viocjjg': vio_loc,
                    'punishPoint': vio_point,
                    'location': vio_address,
                    'time': vio_time,
                    'punishMoney': vio_money,
                    'paystat': '1',
                    'state': str(vio_status),
                    'viocode': vio_code
                }

                vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': status
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败
        if 'status' in data:
            origin_status = data['status']

            if origin_status == 22:
                status = 5
                message = '车牌号错误'
            elif origin_status == 23:
                status = 6
                message = '发动机号错误'
            else:
                status = 51
                message = '数据源异常'
        else:
            status = 99
            message = '查询失败'

        vio_dict = {'status': status, 'message': message}

    return vio_dict


# 根据盔甲接口返回数据构造违章数据
def vio_dic_for_kuijia_old(v_number, data, user_ip):
    if data.get('success', False):
        status = '0'

        vio_list = []
        if 'data' in data and 'peccancy' in data['data'] and len(data['data']['peccancy']) > 0 and 'peccancies' in \
                data['data']['peccancy'][0]:
            for vio in data['data']['peccancy'][0]['peccancies']:
                # 缴费状态, 是否换成status, 需要和盔甲确认
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
                    vio_point = vio['point']
                else:
                    vio_point = ''

                # 罚款
                if 'fee' in vio:
                    vio_money = vio['fee']
                else:
                    vio_money = ''

                # 处理机关
                if 'department' in vio:
                    vio_loc = vio['department']
                else:
                    vio_loc = ''

                # 违法代码
                vio_code = ''  # 盔甲不返回违法代码

                # 违法处理状态
                try:
                    if 'state' in vio:
                        vio_status = vio['state']
                    else:
                        vio_status = -1
                except Exception as e:
                    print(e)
                    vio_status = -1

                vio_data = {
                    'reason': vio_activity,
                    'viocjjg': vio_loc,
                    'punishPoint': str(vio_point),
                    'location': vio_address,
                    'time': vio_time,
                    'punishMoney': str(vio_money),
                    'paystat': str(vio_pay),
                    'state': str(vio_status),
                    'viocode': vio_code
                }

                vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': status
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败
        if 'status' in data:
            origin_status = data['status']

            if origin_status in [-1, -41, -6]:
                status = 21
                message = '车辆信息不正确'
            elif origin_status == -3:
                status = 41
                message = '该城市不支持查询'
            elif origin_status in [-5, -42]:
                status = 39
                message = '数据源不稳定, 请稍后再查'
            elif origin_status in [-61, -66]:
                status = 5
                message = '车牌号错误'
            elif origin_status == -7:
                status = 34
                message = '车架号错误'
            elif origin_status == -63:
                status = 6
                message = '发动机号错误'
            elif origin_status == -67:
                status = 42
                message = '该城市不支持外地车牌查询'
            else:
                status = 51
                message = '数据源异常'
        else:
            status = 99
            message = '其它错误'

        vio_dict = {'status': status, 'message': message}

    return vio_dict


# 根据zfb返回数据构造违章数据
def vio_dic_for_zfb_old(v_number, data, user_ip):

    if data.get('state') == 0:
        status = '0'

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

            vio_data = {
                'reason': vio_activity,
                'viocjjg': vio_loc,
                'punishPoint': vio_point,
                'location': vio_address,
                'time': vio_time,
                'punishMoney': vio_money,
                'paystat': '-1',
                'state': '-1',
                'viocode': vio_code
            }

            vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': status
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败
        status = data.get('code', 99)
        message = data.get('msg', 'query error')

        vio_dict = {'status': status, 'message': message}

    return vio_dict


# 根据少帅返回数据构造违章数据
def vio_dic_for_shaoshuai_old(v_number, data, user_ip):
    if data.get('state', '') == 'success':
        status = '0'
        vio_list = []
        if 'historys' in data.get('result', ''):
            for vio in data['result']['historys']:
                # 缴费状态
                try:
                    if '未缴款' in vio.get('fine_status', ''):
                        vio_pay = 0
                    elif '已缴款' in vio.get('fine_status', ''):
                        vio_pay = 1
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
                    vio_point = vio['fen']
                else:
                    vio_point = ''

                # 罚款
                if 'money' in vio:
                    vio_money = vio['money']
                else:
                    vio_money = ''

                # 处理机关
                if 'officer' in vio:
                    vio_loc = vio['officer']
                else:
                    vio_loc = ''

                # 违法代码
                if 'illegal_code' in vio:
                    vio_code = vio['illegal_code']
                else:
                    vio_code = ''

                # 违法处理状态
                try:
                    if 'processStatus' in vio:
                        vio_status = vio['processStatus']
                    else:
                        vio_status = -1
                except Exception as e:
                    print(e)
                    vio_status = -1

                try:
                    if '未处理' in vio.get('fine_status', ''):
                        vio_status = 0
                    elif '已处理' in vio.get('fine_status', ''):
                        vio_status = 1
                    else:
                        vio_status = -1
                except Exception as e:
                    print(e)
                    vio_status = -1

                vio_data = {
                    'reason': vio_activity,
                    'viocjjg': vio_loc,
                    'punishPoint': str(vio_point),
                    'location': str(vio_address),
                    'time': vio_time,
                    'punishMoney': vio_money,
                    'paystat': str(vio_pay),
                    'state': str(vio_status),
                    'viocode': vio_code
                }

                vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': status
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败
        if 'error_code' in data:
            origin_status = data['error_code']

            if origin_status == '50016':
                status = 32
                message = '车牌号或车辆类型错误'
            elif origin_status == '50200':
                status = 36
                message = '车辆信息不正确'
            else:
                status = 51
                message = '数据源异常'
        else:
            status = 99
            message = '其它错误'

        vio_dict = {'status': status, 'message': message}

    return vio_dict


# 根据车务帮返回数据构造违章数据
def vio_dic_for_cwb_old(v_number, data, user_ip):
    if data.get('status_code', -1) == 2000:
        status = '0'
        vio_list = []

        for vio in data.get('historys', ''):
            # 缴费状态
            try:
                if '未缴款' in vio.get('fine_status', ''):
                    vio_pay = 0
                elif '已缴款' in vio.get('fine_status', ''):
                    vio_pay = 1
                else:
                    vio_pay = -1
            except Exception as e:
                print(e)
                vio_pay = -1

            # 已经缴费的违章数据不再返回
            if vio_pay == 1:
                continue

            try:
                if '未处理' in vio.get('fine_status', ''):
                    vio_status = 0
                elif '已处理' in vio.get('fine_status', ''):
                    vio_status = 1
                else:
                    vio_status = -1
            except Exception as e:
                print(e)
                vio_status = -1

            vio_time = vio.get('occur_date', '')  # 违法时间
            vio_address = vio.get('occur_area', '')  # 违法地点
            vio_activity = vio.get('info', '')  # 违法行为
            vio_point = vio.get('fen', '')  # 扣分
            vio_money = vio.get('money', '')  # 罚款
            vio_loc = get_loc_by_vio_id(vio.get('vioid', ''))  # 处理机关
            vio_code = ''  # 违法代码

            vio_data = {
                'reason': vio_activity,
                'viocjjg': vio_loc,
                'punishPoint': str(vio_point),
                'location': str(vio_address),
                'time': vio_time,
                'punishMoney': str(vio_money),
                'paystat': str(vio_pay),
                'state': str(vio_status),
                'viocode': str(vio_code)
            }

            vio_list.append(vio_data)

        feedback = {
            'cars': v_number,
            'requestIp': user_ip,
            'responseTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        result = {
            'platNumber': v_number,
            'punishs': vio_list,
            'status': status
        }

        vio_dict = {'feedback': feedback, 'result': result}
    else:
        # 查询失败

        origin_status = data.get('status_code', -1)

        if origin_status == 5000:
            status = 21
            message = '车辆信息不正确'
        elif origin_status == 5003:
            status = 39
            message = '数据源不稳定, 请稍后再查'
        else:
            status = 51
            message = '数据源异常'

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

                try:
                    vio_info.vio_point = int(float(vio['punishPoint']))
                except Exception as e:
                    print(e)
                try:
                    vio_info.vio_money = int(float(vio['punishMoney']))
                except Exception as e:
                    print(e)

                vio_info.vio_loc = vio['viocjjg']
                vio_info.vio_code = vio['viocode']

                try:
                    deal_status = int(vio['state'])
                    if deal_status == 3:
                        deal_status = 1
                    elif deal_status == -1:
                        deal_status = -1
                    else:
                        deal_status = 0
                except Exception as e:
                    print(e)
                    deal_status = -1

                vio_info.deal_status = deal_status

                try:
                    pay_status = int(vio['paystat'])
                    if pay_status == 2:
                        pay_status = 1
                    elif pay_status == -1:
                        pay_status = -1
                    else:
                        pay_status = 0
                except Exception as e:
                    print(e)
                    pay_status = -1

                vio_info.pay_status = pay_status

                vio_info.save()
    except Exception as e:
        print(e)


# 保存查询日志
def save_log_old(v_number, origin_data, vio_data, user_id, url_id, user_ip, city=''):
    """
    保存典典返回的查询结果到日志
    :param v_number: 车牌号
    :param origin_data: 违章接口返回原始数据
    :param vio_data: 标准化后的违章数据
    :param user_id: 用户id
    :param url_id: 查询url_id, 98表示车辆注册/注销
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

    elif url_id == 99 or ('result' in vio_data and 'status' in vio_data['result'] and
                          int(vio_data['result']['status']) == 0):

        # 查询成功
        log_info.status = 0

    else:

        if 'status' in vio_data:
            log_info.status = vio_data['status']

        if 'message' in vio_data:
            log_info.msg = vio_data['message']

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
            vehicle_set = VehicleInfo.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)

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
        vehicle_set = VehicleInfo.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)

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
            vehicle_info = VehicleInfo()

            vehicle_info.vehicle_number = v_number
            vehicle_info.vehicle_type = v_type
            vehicle_info.vehicle_code = v_code
            vehicle_info.engine_code = e_code
            vehicle_info.city = city
            vehicle_info.user_id = user_id

            vehicle_info.save()

            return {'status': 21, 'message': 'register success'}
    except Exception as e:
        print(e)
        return {'status': 22, 'message': 'register failure'}
