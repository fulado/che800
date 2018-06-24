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

    vio_data = get_violations(data['vehicleNumber'], data['vehicleType'])

    return JsonResponse(vio_data)


# 根据用户提交的信息构造违章返回数据
def get_violations(vehicleNumber, vehicleType):
    try:
        # 建立数据库连接
        db = get_db()

        # 从mongo数据中查询违章数据
        vio_list = get_violation_from_mongodb(vehicleNumber, vehicleType, db)

        # 根据违法代码构造违法数据列表
        vio_data = []
        for vio in vio_list:
            vio_activity = db.v_ViolationCodeDic.find_one({'dm': vio['code']})
            vio_info = {'time': vio['time'], 'position': vio['position'], 'code': vio['code'],
                        'activity': vio_activity['wfxw'], 'point': vio_activity['jfz'], 'money': vio_activity['fke1'],
                        'location': vio['location']}
            vio_data.append(vio_info)

        # 构造返回数据
        result = {'status': 0, 'vehicleNumber': vehicleNumber, 'data': vio_data}
    except Exception as e:
        print(e)
        result = {'status': 21}
    finally:
        return result


# 根据车牌查询违章
def get_violation_from_mongodb(vehicleNumber, vehicleType, db):
    try:
        # 在现场处罚表中查询违章
        result = db.ViolationUp.find({'hphm': vehicleNumber, 'hpzl': vehicleType})

        # 构造返回数据
        vio_list = []
        for item in result:
            vio_info = {'code': item['wfxw'], 'time': item['wfsj'], 'position': item['wfdz'],
                        'location': item['cljgmc']}
            vio_list.append(vio_info)

        # 在非现场处罚表中查询违章
        result = db.SurveilUp.find({'hphm': vehicleNumber, 'hpzl': vehicleType})

        # 构造返回数据
        for item in result:
            vio_info = {'code': item['wfxw'], 'time': item['wfsj'], 'position': item['wfdz'],
                        'location': item['cjjgmc']}
            vio_list.append(vio_info)

        return vio_list
    except Exception as e:
        print(e)
        raise e


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
        mongodb_ip = '192.168.100.240'
        mongodb_port = 27017

        # 创建连接对象
        client = pymongo.MongoClient(host=mongodb_ip, port=mongodb_port)

        # 获得数据库
        vio_db = client.violation

        return vio_db
    except Exception as e:
        print(e)
        raise e
