from django.http import JsonResponse, HttpResponse
from .forms import SearchForm
from .models import UserInfo, LocInfo, VioInfo, VehicleInfo, LogInfo
from .utils import get_vio_from_tj, get_vio_from_chelun, get_vio_from_ddyc, vio_dic_for_ddyc, vio_dic_for_chelun,\
    save_to_loc_db, save_log
from multiprocessing import Queue
from threading import Thread
import time
import hashlib
import pymysql


# 违章查询请求
def violation(request):
    """
    用户查询违章请求
    :param request: post或get方式
    :return: 违章数据, json格式
    """

    # 判断当前时间, 每天00:10 ~ 00.30禁止查询, 系统自动日志
    current_hour = time.localtime().tm_hour
    current_min = time.localtime().tm_min

    if current_hour == 0 and current_min in range(10, 30):
        return JsonResponse({'status': 19})

    # 判断请求ip是否在白名单中
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

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
    sign = hashlib.sha1(sign.encode('utf-8')).hexdigest().upper()

    if sign != data['sign']:
        result = {'status': 12}
        return JsonResponse(result)

    # 查询违章信息
    # print('查询车辆, 号牌号码: %s, 号牌种类: %s' % (data['vehicleNumber'], data['vehicleType']))
    vio_data = get_violations(v_number=data['vehicleNumber'], v_type=data['vehicleType'],
                              v_code=data['vehicleCode'], e_code=data['engineCode'], city=data['city'],
                              user_id=user.id, user_ip=user_ip)

    # 根据查询结果记录车辆信息
    # 将车辆信息保存都本地数据库
    # 判断本地数据库中是否已经存在该车辆信息
    # 车辆信息在第一次保存到数据库中时, 默认无效, 无效车辆在下次查询同一车辆时, 需要更新车辆信息,
    # 车辆信息在完成一次正确查询后, 后变为有效, 有效车辆信息应该每天更新一次
    # try:
    #     vehicle = VehicleInfo.objects.filter(vehicle_number=data['vehicleNumber']).filter(vehicle_type=
    #                                                                                       data['vehicleType'])
    #     if vehicle.exists():
    #         vehicle = vehicle[0]
    #         vehicle.query_counter += 1
    #         if not vehicle.status:
    #             vehicle.vehicle_code = data['vehicleCode']
    #             vehicle.engine_code = data['engineCode']
    #             vehicle.city = data['city']
    #             if not vio_data['status']:
    #                 vehicle.status = 1
    #     else:
    #         vehicle = VehicleInfo()
    #         vehicle.vehicle_number = data['vehicleNumber']
    #         vehicle.vehicle_type = data['vehicleType']
    #         vehicle.vehicle_code = data['vehicleCode']
    #         vehicle.engine_code = data['engineCode']
    #         vehicle.city = data['city']
    #         vehicle.create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #
    #     vehicle.save()
    # except Exception as e:
    #     print(e)

    # 记录查询日志

    return JsonResponse(vio_data)


# 根据车辆信息查询违章
def get_violations(v_number, v_type=2, v_code='', e_code='', city='', user_id=99, user_ip='127.0.0.1'):
    """
    根据车辆信息调用不同的接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :param city: 查询城市
    :return: 违章数据, json格式
    """
    # 将车辆类型转为int型
    v_type = int(v_type)

    # 先从本地数据库查询, 如果本地数据库没有该违章数据, 再通过接口查询
    try:
        vio_info_list = VioInfo.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)
    except Exception as e:
        print(e)
    else:
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

            # 保存日志
            save_log(v_number, '', user_id, 99, user_ip)

            return {'vehicleNumber': v_number, 'status': 0, 'data': vio_list}

    # 获取查询城市和查询url_id
    # 目前看来这个功能没啥用, 暂时先把它省略了吧, 只判断车牌开头的城市简称, 根据这个确定调用哪个查询接口, 现在只查询天津的车
    # 将车牌类型转为字符串'02'
    if v_type < 10:
        v_type = '0%d' % v_type
    else:
        v_type = str(v_type)

    try:
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
            url_id = 2
        else:
            # city = loc_info.loc_name
            url_id = loc_info.url_id.id
    except Exception as e:
        print(e)
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
        data = vio_dic_for_ddyc(v_number, data)
        # print('%s -- ddyc api' % v_number)

    else:

        data = get_vio_from_chelun(v_number, v_type, v_code, e_code)
        # print(data)
        # 保存日志
        save_log(v_number, data, user_id, url_id, user_ip)
        data = vio_dic_for_chelun(v_number, data)

        # print('%s -- chelun api' % v_number)
    # print(data['status'])

    # 如果查询成功, 保存数据到本地数据库
    if data['status'] == 0:
        save_to_loc_db(data, v_number, v_type)

    # 不能直接返回data, 应该把data再次封装后再返回
    return data


# 车辆读取线程
def get_vehicle_thread(v_queue):

    # 循环3次, 每次只查询之前查询失败的车辆
    for i in range(3):
        # 查询数据库中的车辆数据, 已经查询成功的不再查询
        vehicle_list = VehicleInfo.objects.filter(status=0)

        # 查询违章
        for vehicle in vehicle_list:
            # 将车辆信息放入队列
            v_queue.put(vehicle, True)


# 违章查询线程
def query_thread(v_queue):
    while True:
        try:
            # print('query thread %d start' % t_id)
            vehicle = v_queue.get(True, 5)
            data = get_violations(vehicle.vehicle_number, vehicle.vehicle_type, vehicle.vehicle_code,
                                  vehicle.engine_code, vehicle.city)

            # 如果查询成功, 将讲车辆查询状态置为1
            if data['status'] == 0:
                vehicle.status = 1
                vehicle.save()

        except Exception as e:
            print(e)
            break


# 定时任务, 查询车辆库中车辆违章数据
def query_vio_auto():
    # print('auto query start')

    # 创建车辆队列
    vehicle_queue = Queue(5)

    # 创建车辆读取线程
    t_get_vehicle_thread = Thread(target=get_vehicle_thread, args=(vehicle_queue,))
    t_get_vehicle_thread.start()

    # 创建5个车辆查询线程
    for i in range(5):
        t_query_thread = Thread(target=query_thread, args=(vehicle_queue,))
        t_query_thread.start()

    # print('auto query complete')


# 定时任务, 备份并初始化违章表和日志表
def backup_log():

    # 数据库连接信息
    # host = '127.0.0.1'
    host = '172.21.0.2'
    port = 3306
    user = 'root'
    password = 'Init1234'
    # password = 'xiaobai'
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

        # 日志表改名
        sql = 'RENAME TABLE vio_sch_loginfo TO vio_sch_loginfo_%s;' % name_time
        cs.execute(sql)

        # 新建日志表
        sql = """CREATE TABLE `vio_sch_loginfo` (
                      `id` int(11) NOT NULL AUTO_INCREMENT,
                      `query_time` datetime(6) DEFAULT NULL,
                      `status` int(11) DEFAULT NULL,
                      `comments` varchar(200) DEFAULT NULL,
                      `url_id` int(11) DEFAULT NULL,
                      `user_id` int(11) DEFAULT NULL,
                      `vehicle_number` varchar(20) DEFAULT NULL,
                      `ip` varchar(20) DEFAULT NULL,
                      PRIMARY KEY (`id`),
                      FOREIGN KEY (`url_id`) REFERENCES `vio_sch_urlinfo` (`id`),
                      FOREIGN KEY (`user_id`) REFERENCES `vio_sch_userinfo` (`id`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        cs.execute(sql)

        # 违章表改名
        sql = 'RENAME TABLE vio_sch_vioinfo TO vio_sch_vioinfo_%s;' % name_time
        cs.execute(sql)

        # 新建违章表
        sql = """CREATE TABLE `vio_sch_vioinfo` (
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
                    PRIMARY KEY (`id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=6238 DEFAULT CHARSET=utf8mb4"""
        cs.execute(sql)
    except Exception as e:
        print(e)

    finally:
        # 关闭Cursor
        cs.close()

        # 关闭连接
        conn.close()

        print('Initial complete')


# 定时任务, 重置车辆违章查询状态status为0
def reset_status():
    VehicleInfo.objects.all().update(status=0)


# 定时任务, 测试
def test_task():
    loginfo = LogInfo()

    loginfo.vehicle_number = 'test123'
    loginfo.user_id = 99
    loginfo.url_id = 99
    loginfo.query_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    loginfo.comments = '123'
    loginfo.ip = '123,456.789.1'

    loginfo.save()


# 负载均衡测试
def nginx_test(request):
    return HttpResponse('<h1>server 02</h1>')
