# views.py
"""
天津违章查询
"""
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .forms import SearchForm
from .models import UserInfo, IpInfo, VioCode
import time
import hashlib
import pymongo


# just for test
def violation(request):

    # 判断请求ip是否在白名单中
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        ip_addr = request.META['HTTP_X_FORWARDED_FOR']
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
        result = {'status': 99, 'msg': '无效的请求数据'}
        return JsonResponse(result)

    # 获取请求数据
    data = form_obj.clean()

    # 判断用户是否存在, 如果不存在返回11
    try:
        user = UserInfo.objects.get(username=data['username'])
    except Exception as e:
        print(e)
        result = {'status': 11, 'msg': '用户名不存在'}
        return JsonResponse(result)

    # 判断用户传入的时间戳是否可以转化为int类型
    try:
        timestamp_user = int(data['timestamp'])
    except Exception as e:
        print(e)
        result = {'status': 15, 'msg': '时间戳格式错误'}
        return JsonResponse(result)

    # 判断时间戳是否超时, 默认5分钟
    if int(time.time()) - timestamp_user > 60 * 5:
        result = {'status': 16, 'msg': '时间戳超时'}
        return JsonResponse(result)

    # 校验sign
    sign = '%s%d%s' % (user.username, timestamp_user, user.password)
    # print(sign)
    sign = hashlib.sha1(sign.encode('utf-8')).hexdigest()

    if sign != data['sign']:
        result = {'status': 12, 'msg': '签名错误'}
        return JsonResponse(result)

    # 查询违章信息
    # print('查询车辆, 号牌号码: %s, 号牌种类: %s' % (data['vehicleNumber'], data['vehicleType']))

    # 判断用户传递的参数中是否包含发动机号
    if 'engineCode' in data:
        vio_data = get_violations(data['vehicleNumber'], data['vehicleType'], data['engineCode'])
    else:
        vio_data = get_violations(data['vehicleNumber'], data['vehicleType'])

    return JsonResponse(vio_data)


# 根据用户提交的信息构造违章返回数据
def get_violations(v_number, v_type, e_code=''):

    try:
        # 建立数据库连接
        db = get_db()

        # 校验车辆信息
        check_result = check_vehicle(v_number, v_type, e_code, db)

        if check_result == 0:

            # 从mongo数据中查询违章数据
            vio_list = get_violation_from_mongodb(v_number, v_type, db)

            # 根据违法代码构造违法数据列表
            vio_data = []
            for vio in vio_list:
                vio_activity = db.v_ViolationCodeDic.find_one({'dm': vio['code']})
                vio_info = {
                    'time': vio['time'],
                    'position': vio['position'],
                    'code': vio['code'],
                    'activity': vio_activity['wfxw'],
                    'point': vio_activity['jfz'],
                    'money': vio_activity['fke1'],
                    'location': vio['location'],
                    'deal': vio['deal'],
                    'pay': vio['pay']
                }
                vio_data.append(vio_info)

            # 构造返回数据
            result = {'status': 0, 'vehicleNumber': v_number, 'data': vio_data}

        elif check_result == 1:

            result = {'status': 22, 'msg': '车牌号或车辆类型错误'}

        else:

            result = {'status': 23, 'msg': '发动机号错误'}

    except Exception as e:
        print(e)
        result = {'status': 21, 'msg': '交管数据维护中, 请稍后再试'}
    finally:
        return result


# 校验车牌号, 车辆类型, 发动机号
def check_vehicle(v_number, v_type, e_code, db):
    """
    查询VehicleUp表, 校验津牌车辆的车牌号, 车辆类型, 发动机号, 外地号牌车辆不做校验
    :param v_number: 号牌号码
    :param v_type: 车辆类型
    :param e_code: 发动机号
    :param db: 数据库连接
    :return: 0-正确, 1-车牌号或车辆类型错误, 2-发动机号错误, 外地车牌不校验直接返回0
    """
    # 如果车牌号长度小于2, 返回1-车牌号错误
    if len(v_number) < 2 or len(v_type) != 2:
        return 1

    # 如果不是津牌, 直接返回0, 否则判断发动机号是否为空, 如果为空, 返回2-发动机号错误
    if v_number[0] != '津':
        return 0
    elif e_code == '':
        return 2

    try:
        # 查询车辆
        vehicle_info = db.VehicleUp.find_one({'hphm': v_number[1:], 'hpzl': v_type})

        # 如果查询不到返回1-车牌号或车辆类型错误
        if not vehicle_info:
            return 1

        # 判断发动机号是否正确
        if e_code == vehicle_info['fdjh']:
            return 0
        else:
            return 2

    except Exception as e:
        raise e


# 根据车牌查询违章
def get_violation_from_mongodb(v_number, v_type, db):
    try:
        # 在现场处罚表中查询违章, violation并非现场处罚表, 而是所有已处理车辆均会进入该表, 但目前表中数据非常乱, 甚至有很多重复数据
        # 因此暂时不从该表中查询
        # cursor = db.ViolationUp.find({'hphm': v_number, 'hpzl': v_type})

        # 构造返回数据
        vio_list = []
        # for item in cursor:
        #     vio_info = {'code': item['wfxw'], 'time': item['wfsj'], 'position': item['wfdz'],
        #                 'location': item['cljgmc'], 'deal': '', 'pay': item['jkbj']}
        #     vio_list.append(vio_info)

        # 在非现场处罚表中查询违章
        cursor = db.SurveilUp.find({'hphm': v_number, 'hpzl': v_type})

        # 构造返回数据
        for item in cursor:
            # 已交款或这无需交款数据不返回
            if item['jkbj'] in ['1', '9']:
                continue

            vio_info = {'code': item['wfxw'], 'time': item['wfsj'], 'position': item['wfdz'],
                        'location': item['cjjgmc'], 'deal': item['clbj'], 'pay': item['jkbj']}
            vio_list.append(vio_info)

        return vio_list
    except Exception as e:
        raise e
    finally:
        cursor.close()


# 根据违法代码查询具体违法行为, 扣分, 罚款金额
# def get_activity_by_code(vio_code, db):
#     try:
#         vio_obj = db.v_ViolationCodeDic.findOne({'dm': vio_code})
#         return vio_obj['wfxw'], vio_obj['jfz'], vio_obj['fke1']
#     except Exception as e:
#         print(e)
#         raise e


# 获得MongoDB数据库连接
def get_db():
    try:
        # mongodb数据库ip, 端口
        mongodb_ip = '192.168.100.234'
        mongodb_port = 27017

        # 创建连接对象
        client = pymongo.MongoClient(host=mongodb_ip, port=mongodb_port)

        # 获得数据库
        vio_db = client.violation

        return vio_db
    except Exception as e:
        print(e)
        raise e
