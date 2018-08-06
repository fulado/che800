import re
from multiprocessing import Queue
from threading import Thread

import requests

from .models import VioInfo, VehicleInfo


# 查询违章, 返回html
def get_raw_vio_data(v_number, p_color=1):

    url = 'http://jtzf.cq.gov.cn/jeecms/illegal.jspx'

    params = {
        'plateNumber': v_number,
        'plateColor': p_color
    }

    response_data = requests.get(url=url, params=params)

    return response_data


# 使用正则, 从html中获取违章数据
def get_std_vio_data(raw_vio_data):

    p = re.compile(r'<td align="center">(.*)</td>')

    # 获取违章数据列表
    vio_list = p.findall(raw_vio_data)

    # 构造违章数据列表
    std_vio_list = []

    for i in range(0, len(vio_list), 3):
        std_vio_list.append(vio_list[i: i+3])

    return std_vio_list


# 保存违章结果到数据库
def save_vio_to_db(v_number, std_vio_list):
    for vio_data in std_vio_list:
        vio_info = VioInfo()

        try:
            vio_info.vehicle_number = v_number
            vio_info.vio_time = vio_data[0]
            vio_info.vio_position = vio_data[1]
            vio_info.vio_activity = vio_data[2]
            vio_info.vio_point = None
            vio_info.vio_money = None

            vio_info.save()
        except Exception as e:
            print(e)


# 车辆读取线程
def get_vehicle_thread(v_queue):

    # 循环3次, 每次只查询之前查询失败的车辆
    for i in range(3):
        # 查询数据库中的车辆数据, 已经查询成功的不再查询
        vehicle_list = VehicleInfo.objects.filter(vehicle_number__contains='渝').filter(spider_status=False)

        # 查询违章
        for vehicle in vehicle_list:
            # 将车辆信息放入队列
            v_queue.put(vehicle, True)


# 违章查询线程
def query_thread(v_queue):
    while True:
        try:
            # 从队列中获取车辆对象
            vehicle = v_queue.get(True, 5)

            # 开始查询
            raw_data = get_raw_vio_data(vehicle.vehicle_number)
            print(raw_data.status_code)

            if raw_data.status_code == 200:
                vio_list = get_std_vio_data(raw_data.content.decode())
                vehicle.spider_status = 1
                vehicle.save()
                print(vio_list)

            if len(vio_list) != 0:
                save_vio_to_db(vehicle.vehicle_number, vio_list)

        except Exception as e:
            print(e)
            break


# 主程序
def main():
    print('spider is working now.')

    # 创建车辆队列
    vehicle_queue = Queue(5)

    # 创建车辆读取线程
    t_get_vehicle_thread = Thread(target=get_vehicle_thread, args=(vehicle_queue,))
    t_get_vehicle_thread.start()

    # 创建5个车辆查询线程
    for i in range(20):
        t_query_thread = Thread(target=query_thread, args=(vehicle_queue,))
        t_query_thread.start()


if __name__ == '__main__':
    main()
