import base64
import hashlib
import json
import time

from django.http import HttpResponse

from .models import UserInfo, LogInfo
from .driver import Driver

from .utils import check_user, create_response_data, get_db, decode_data


# 用户登录
def login_service(request):

    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    # 不接收get方式请求
    if request.method == 'GET':
        response_data = {'status': 14, 'message': '请求方式错误'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))

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

        return HttpResponse(response_data)

    # 根据用户名密码和时间戳计算token
    token = '%s%d%s' % (username, user.timestamp, password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()
    print(token)
    # 构造返回数据
    response_data = base64.b64encode(json.dumps({'status': 9, 'token': token}).encode('utf-8'))

    return HttpResponse(response_data)


# 查询违章
def violation_service(request):

    request_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    # 获取用户传递的参数
    param = request.POST.get('param', '')

    response_data = check_user(param)

    if response_data.get('status'):
        response_data = create_response_data(response_data)
        return HttpResponse(response_data)

    param = decode_data(param)
    # 获取车辆数据
    try:
        v_data = param['cars'][0]
    except Exception as e:
        print(e)
        response_data = {'status': 21, 'message': '车辆信息不正确'}
        response_data = create_response_data(response_data)
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
        response_data = create_response_data(response_data)
        return HttpResponse(response_data)

    # 判断车牌号
    try:
        v_number = v_data['platNumber']
        if v_type == '02' and len(v_number) < 7:
            raise Exception
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': '车牌号错误'}
        response_data = create_response_data(response_data)
        return HttpResponse(response_data)

    # 判断车辆识别代号, 发动机号
    try:
        e_code = v_data['engineNumber']
    except Exception as e:
        print(e)
        response_data = {'status': 6, 'message': '发动机号错误'}
        response_data = create_response_data(response_data)
        return HttpResponse(response_data)

    response_data = get_violations(v_number, v_type, e_code, request_time, user_ip)
    # print(response_data)
    response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))

    response_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # 保存日志
    try:
        log_info = LogInfo()

        log_info.request_time = request_time
        log_info.response_time = response_time
        log_info.v_number = v_number
        log_info.v_type = v_type

        log_info.save()
    except Exception as e:
        print(e)

    return HttpResponse(response_data)


# 根据用户提交的信息构造违章返回数据
def get_violations(v_number, v_type, e_code='', request_time='', ip_addr=''):

    try:
        # 建立数据库连接
        db = get_db()

        # 校验车辆信息
        vehicle_info = check_vehicle(v_number, v_type, e_code, db)

        if vehicle_info:

            # 从mongo数据中查询违章数据
            vio_list = get_violation_from_mongodb(v_number, v_type, db)

            # 根据违法代码构造违法数据列表
            vio_data = []
            for vio in vio_list:
                vio_activity = db.v_ViolationCodeDic.find_one({'dm': vio['code']})
                vio_info = {
                    'time': vio['time'],
                    'location': vio['position'],
                    'wzcode': vio['code'],
                    'reason': vio_activity['wfxw'],
                    'punishPoint': vio_activity['jfz'],
                    'punishMoney': vio_activity['fke1'],
                    'state': vio['location'],
                    'deal': vio['deal'],
                    'paystat': vio['pay']
                }
                vio_data.append(vio_info)

            result = {
                'punishs': vio_data,
                'status': 0,
                'platNumber': v_number
            }

            # 构造返回数据
            feedback = {
                'requestTime': request_time,
                'cars': v_number,
                'requestIp': ip_addr,
                'responseTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'yxqz': vehicle_info['yxqz'],
                'enginenums': vehicle_info['enginenums'],
                'vins': vehicle_info['vins'],
                'zts': vehicle_info['zts'],
                'hpzls': vehicle_info['hpzls'],
            }

            result = {
                'feedback': feedback,
                'result': [result, ]
            }

        else:

            result = {'status': 6, 'message': '发动机号错误'}

    except Exception as e:
        print(e)
        result = {'status': 99, 'message': '其它错误'}
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
        return False

    # 如果不是津牌, 直接返回0, 否则判断发动机号是否为空, 如果为空, 返回2-发动机号错误
    if v_number[0] != '津':
        v_info = {'yxqz': '',
                  'enginenums': '',
                  'vins': '',
                  'zts': '',
                  'hpzls': v_type
                  }
        return v_info
    elif e_code == '':
        return False

    e_code = e_code.strip('0')

    try:
        # 查询车辆
        vehicle_info = db.VehicleUp.find_one({'hphm': v_number[1:], 'hpzl': v_type})

        # 如果查询不到返回1-车牌号或车辆类型错误
        if not vehicle_info:
            return False

        # 判断发动机号是否正确
        if e_code in vehicle_info['fdjh']:
            v_info = {
                'yxqz': vehicle_info['yxqz'],
                'enginenums': vehicle_info['fdjh'],
                'vins': vehicle_info['clsbdh'],
                'zts': vehicle_info['zt'],
                'hpzls': vehicle_info['hpzl']
            }
            return v_info
        else:
            return False

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

            vio_info = {
                'code': item['wfxw'],
                'time': item['wfsj'],
                'position': item['wfdz'],
                'location': item['cjjgmc'],
                'deal': item['clbj'],
                'pay': item['jkbj']
            }
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
# def get_db():
#     try:
#         # mongodb数据库ip, 端口
#         mongodb_ip = '192.168.100.234'
#         mongodb_port = 27017
#
#         # 创建连接对象
#         client = pymongo.MongoClient(host=mongodb_ip, port=mongodb_port)
#
#         # 获得数据库
#         vio_db = client.violation
#
#         return vio_db
#     except Exception as e:
#         print(e)
#         raise e


# 查询驾驶人信息
def driver_service(request):

    # 获取用户传递的参数
    param = request.POST.get('param', '')

    response_data = check_user(param)

    if response_data.get('status'):
        response_data = create_response_data(response_data)
        return HttpResponse(response_data)

    param_dict = decode_data(param)
    driver_name = param_dict.get('xm')
    file_id = param_dict.get('dabh')

    driver = Driver(driver_name, file_id)

    db = get_db()
    print(db)
    driver.get_driver_info(db)

    if driver.is_exist:
        driver.create_driver_info()

    response_data = create_response_data(driver.license_info)
    return HttpResponse(response_data)
