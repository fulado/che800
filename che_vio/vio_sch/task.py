from .models import VehicleInfo
from .views import get_violations
from django.db import connection
from threading import Thread
from multiprocessing import Queue

import datetime
import pymysql
import time


# 定时任务, 重置车辆违章查询状态status为0
def reset_status():
    # 判断连接是否可用, 如不可用关闭连接
    try:
        connection.connection.ping()
    except:
        connection.close()
    finally:
        VehicleInfo.objects.all().update(status=0, spider_status=False)


# 定时任务，清楚10天未查询的车辆信息
def delete_vehicle_over_dead_date():
    dead_date = datetime.datetime.today() - datetime.timedelta(days=10)

    try:
        VehicleInfo.objects.filter(update_time__lt=dead_date).delete()
    except Exception as e:
        print(e)


# 定时任务, 备份并初始化违章表和日志表
def backup_vio_data_avis():

    # 数据库连接信息
    host = 'bj-cdb-gq8xi5ya.sql.tencentcdb.com'
    port = 63226
    # host = '172.21.0.2'
    # port = 3306
    user = 'root'
    password = 'Init1234'
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

        # 创建备份表
        sql = 'CREATE TABLE vio_sch_vioinfoavis_%s LIKE vio_sch_vioinfoavis;' % name_time
        cs.execute(sql)

        # 备份数据
        sql = 'INSERT INTO vio_sch_vioinfoavis_%s SELECT * FROM vio_sch_vioinfoavis;' % name_time
        cs.execute(sql)

    except Exception as e:
        print(e)

    finally:
        # 关闭Cursor
        cs.close()

        conn.commit()

        # 关闭连接
        conn.close()


# 车辆读取线程
def get_vehicle_thread_yiqi(v_queue):

    # 循环3次, 每次只查询之前查询失败的车辆
    for i in range(3):
        # 查询数据库中的车辆数据, 已经查询成功的不再查询
        try:
            connection.connection.ping()
        except:
            connection.close()
        finally:
            vehicle_list = VehicleInfo.objects.filter(status=0, user_id=26)

        # 查询违章
        for vehicle in vehicle_list:
            # 将车辆信息放入队列
            # print(vehicle.vehicle_number)
            v_queue.put(vehicle, True)


# 违章查询线程
def query_thread_yiqi(v_queue, city):
    print('%s auto query yiqi start.' % city)
    while True:
        try:
            vehicle = v_queue.get(True, 30)

            data = get_violations(vehicle.vehicle_number, vehicle.vehicle_type, vehicle.vehicle_code,
                                  vehicle.engine_code, vehicle.city, '99', '127.0.0.1', True)

            # 如果查询成功, 将车辆查询状态置为1
            if data['status'] == 0:
                vehicle.status = 1
                vehicle.save()
            elif data['status'] in (32, 33, 34, 35, 36):
                vehicle.status = data['status']
                vehicle.save()

        except Exception as e:
            print(e)
            print('%s auto query complete.' % city)
            break


# 定时任务, 查询一汽车辆
def query_vio_auto_yiqi():

    # 创建车辆队列
    vehicle_queue = Queue(5)

    # 创建车辆读取线程
    t_get_vehicle_thread = Thread(target=get_vehicle_thread_yiqi, args=(vehicle_queue,))
    t_get_vehicle_thread.start()

    # 创建5个车辆查询线程
    for i in range(3):
        t_query_thread = Thread(target=query_thread_yiqi, args=(vehicle_queue, 'yiqi_%d' % (i + 1)))
        t_query_thread.start()


if __name__ == '__main__':
    backup_vio_data_avis()
