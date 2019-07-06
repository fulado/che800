import time
import hashlib

from django.http import JsonResponse

from .forms import SearchForm
from .models import UserInfo, VehicleInfo
from .utils import save_error_log


# 违章查询请求
def register(request):
    """
    用户查询违章请求
    :param request: post或get方式
    :return: 违章数据, json格式
    """
    # 打印请求头中的所有内容
    # hearders = request.META.items()
    #
    # for k, v in hearders:
    #     print(k, v)
    #
    # print('*' * 50)

    # 判断当前时间, 每天02:00 ~ 02:20禁止查询, 系统自动日志
    current_hour = time.localtime().tm_hour
    current_min = time.localtime().tm_min

    # 判断请求ip是否在白名单中
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    if current_hour == 2 and current_min in range(0, 20):
        save_error_log(19, '系统维护中, 请稍后访问', '', user_ip)
        return JsonResponse({'status': 19, 'msg': '系统维护中, 请稍后访问'})

    # print(ip_addr)

    # 如果ip不在白名单返回状态码14, 暂不校验ip
    # if not IpInfo.objects.filter(ip_addr=ip_addr).exists():
    #     result = {'status': 14}
    #     return JsonResponse(result)

    # 获取请求表单对象
    if request.method == 'GET':
        form_obj = SearchForm(request.GET)
    else:
        form_obj = SearchForm(request.POST)

    # 表单数据无效
    if not form_obj.is_valid():
        result = {'status': 99, 'msg': '请求数据无效'}
        save_error_log(99, '请求数据无效', '', user_ip)
        return JsonResponse(result)

    # 获取请求数据
    data = form_obj.clean()

    # 判断用户是否存在, 如果不存在返回11
    try:
        user = UserInfo.objects.get(username=data['username'])
    except Exception as e:
        print(e)
        result = {'status': 11, 'msg': '用户不存在'}
        save_error_log(11, '用户不存在', '', user_ip)
        return JsonResponse(result)

    # 判断用户传入的时间戳是否可以转化为int类型
    try:
        timestamp_user = int(data['timestamp'])
    except Exception as e:
        print(e)
        result = {'status': 15, 'msg': '时间戳格式错误'}
        save_error_log(15, '时间戳格式错误', user.id, user_ip)
        return JsonResponse(result)

    # 判断时间戳是否超时, 默认5分钟
    if int(time.time()) - timestamp_user > 60 * 5 or int(time.time()) < timestamp_user - 120:
        result = {'status': 16, 'msg': '时间戳超时'}
        save_error_log(16, '时间戳超时', user.id, user_ip)
        return JsonResponse(result)

    # 校验sign
    sign = '%s%d%s' % (user.username, timestamp_user, user.password)
    # print(sign)
    sign = hashlib.sha1(sign.encode('utf-8')).hexdigest().upper()

    if sign != data['sign']:
        result = {'status': 12, 'msg': 'sign签名错误'}
        save_error_log(12, 'sign签名错误', user.id, user_ip)
        return JsonResponse(result)

    # 查询违章信息
    # print('查询车辆, 号牌号码: %s, 号牌种类: %s' % (data['vehicleNumber'], data['vehicleType']))
    result = vehicle_register(v_number=data['vehicleNumber'], v_type=data['vehicleType'], v_code=data['vehicleCode'],
                              e_code=data['engineCode'], status=1, user_id=user.id,  city=data['city'])

    return JsonResponse(result)


# 违章查询请求
def unregister(request):
    """
    用户查询违章请求
    :param request: post或get方式
    :return: 违章数据, json格式
    """

    # 判断当前时间, 每天02:00 ~ 02:20禁止查询, 系统自动日志
    current_hour = time.localtime().tm_hour
    current_min = time.localtime().tm_min

    # 判断请求ip是否在白名单中
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    if current_hour == 2 and current_min in range(0, 20):
        save_error_log(19, '系统维护中, 请稍后访问', '', user_ip)
        return JsonResponse({'status': 19, 'msg': '系统维护中, 请稍后访问'})

    # print(ip_addr)

    # 如果ip不在白名单返回状态码14, 暂不校验ip
    # if not IpInfo.objects.filter(ip_addr=ip_addr).exists():
    #     result = {'status': 14}
    #     return JsonResponse(result)

    # 获取请求表单对象
    if request.method == 'GET':
        form_obj = SearchForm(request.GET)
    else:
        form_obj = SearchForm(request.POST)

    # 表单数据无效
    if not form_obj.is_valid():
        result = {'status': 99, 'msg': '请求数据无效'}
        save_error_log(99, '请求数据无效', '', user_ip)
        return JsonResponse(result)

    # 获取请求数据
    data = form_obj.clean()

    # 判断用户是否存在, 如果不存在返回11
    try:
        user = UserInfo.objects.get(username=data['username'])
    except Exception as e:
        print(e)
        result = {'status': 11, 'msg': '用户不存在'}
        save_error_log(11, '用户不存在', '', user_ip)
        return JsonResponse(result)

    # 判断用户传入的时间戳是否可以转化为int类型
    try:
        timestamp_user = int(data['timestamp'])
    except Exception as e:
        print(e)
        result = {'status': 15, 'msg': '时间戳格式错误'}
        save_error_log(15, '时间戳格式错误', user.id, user_ip)
        return JsonResponse(result)

    # 判断时间戳是否超时, 默认5分钟
    if int(time.time()) - timestamp_user > 60 * 5 or int(time.time()) < timestamp_user - 120:
        result = {'status': 16, 'msg': '时间戳超时'}
        save_error_log(16, '时间戳超时', user.id, user_ip)
        return JsonResponse(result)

    # 校验sign
    sign = '%s%d%s' % (user.username, timestamp_user, user.password)
    # print(sign)
    sign = hashlib.sha1(sign.encode('utf-8')).hexdigest().upper()

    if sign != data['sign']:
        result = {'status': 12, 'msg': 'sign签名错误'}
        save_error_log(12, 'sign签名错误', user.id, user_ip)
        return JsonResponse(result)

    # 查询违章信息
    # print('查询车辆, 号牌号码: %s, 号牌种类: %s' % (data['vehicleNumber'], data['vehicleType']))
    result = vehicle_register(v_number=data['vehicleNumber'], v_type=data['vehicleType'], v_code=data['vehicleCode'],
                              e_code=data['engineCode'], status=2, user_id=user.id,  city=data['city'])

    return JsonResponse(result)


# 车辆注册/注销
def vehicle_register(v_number, v_type, v_code, e_code, status, user_id, city=''):
    """
    接受用户发送的车辆信息, 根据status选择注册或注销, 1-注册, 2-注销
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :param status: 注册/注销, 1-注册, 2-注销
    :param city: 运营城市
    :param user_id: 用户id
    :return: 注册是否成功, json格式
    """
    if status not in [1, 2]:
        status = 1

    # 注销
    if status == 2:
        try:
            vehicle_set = VehicleInfo.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)

            if vehicle_set.exists():
                vehicle_set.delete()
                return {'status': 0, 'message': '车辆注销成功'}
            else:
                return {'status': 21, 'message': '该车辆未注册'}
        except Exception as e:
            print(e)
            return {'status': 22, 'message': '车辆注销失败'}

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

                return {'status': 0, 'message': '车辆注册成功'}
            else:
                return {'status': 11, 'message': '该车辆已经注册'}
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

            return {'status': 0, 'message': '车辆注册成功'}
    except Exception as e:
        print(e)
        return {'status': 12, 'message': '车辆注册失败'}
