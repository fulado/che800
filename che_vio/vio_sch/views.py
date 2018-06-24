from django.http import JsonResponse
from .forms import SearchForm
from .models import UserInfo, LocInfo
from .utils import get_vio_from_chelun, get_vio_from_ddyc, vio_dic_for_ddyc, vio_dic_for_chelun
import time
import hashlib
import json


# 违章查询请求
def violation(request):
    """
    用户查询违章请求
    :param request: post或get方式
    :return: 违章数据, json格式
    """

    # 判断请求ip是否在白名单中
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        ip_addr = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        ip_addr = request.META['REMOTE_ADDR']
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
        result = {'status': 99}
        return JsonResponse(result)

    # 获取请求数据
    data = form_obj.clean()

    # 判断用户是否存在, 如果不存在返回11
    try:
        user = UserInfo.objects.get(username=data['username'])
    except Exception as e:
        print(e)
        result = {'status': 11}
        return JsonResponse(result)

    # 判断用户传入的时间戳是否可以转化为int类型
    try:
        timestamp_user = int(data['timestamp'])
    except Exception as e:
        print(e)
        result = {'status': 15}
        return JsonResponse(result)

    # 判断时间戳是否超时, 默认5分钟
    if int(time.time()) - timestamp_user > 60 * 5:
        result = {'status': 15}
        return JsonResponse(result)

    # 校验sign
    sign = '%s%d%s' % (user.username, timestamp_user, user.password)
    # print(sign)
    sign = hashlib.sha1(sign.encode('utf-8')).hexdigest()
    print(sign)
    if sign != data['sign']:
        result = {'status': 12}
        return JsonResponse(result)

    # 查询违章信息
    # print('查询车辆, 号牌号码: %s, 号牌种类: %s' % (data['vehicleNumber'], data['vehicleType']))

    vio_data = get_violations(data['vehicleNumber'], data['vehicleType'], data['engineCode'], data['vehicleCode'],
                              data['city'])

    return JsonResponse(vio_data)


# 根据车辆信息查询违章
def get_violations(v_number, v_type='02', e_code='', vin='', city=''):
    """
    根据车辆信息调用不同的接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param e_code: 发动机号
    :param vin: 车架号
    :param city: 查询城市
    :return: 违章数据, json格式
    """
    # 获取查询城市和查询url_id
    # 目前看来这个功能没啥用, 暂时先把它省略了吧, 只判断车牌开头的城市简称, 根据这个确定调用哪个查询接口
    try:
        city = ''  # 未来如有需要在修改次功能
        if city != '':
            loc_info = LocInfo.objects.get(loc_name__contains=city)
        else:
            short_name = v_number[0]
            loc_info = LocInfo.objects.get(short_name=short_name)

        # city = loc_info.loc_name
        url_id = loc_info.url_id
    except Exception as e:
        print(e)
        return {'status': 999}  # 查询城市错误

    # 根据url_id调用不同接口, 1-天津接口, 2-典典接口, 3-车轮接口
    if url_id == 1:
        pass
    elif url_id == 2:
        data = get_vio_from_ddyc(v_number, v_type, e_code, vin, city)
        data = vio_dic_for_ddyc(v_number, data)
    else:
        data = get_vio_from_chelun(v_number, v_type, e_code, vin)
        data = vio_dic_for_chelun(v_number, data)

    # 不能直接返回data, 应该把data再次封装后再返回
    return data

