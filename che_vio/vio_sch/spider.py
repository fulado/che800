import re
from multiprocessing import Queue
from threading import Thread

import requests

from .models import VioInfo, VehicleInfo


PUNISH_DIC = {
    '小型车超速（即时速度151-180<含> Km/h）（限速100）': 500,
    '小型车超速（即时速度133-150<含> Km/h）（限速100）': 200,
    '小型车超速（即时速度133-144<含>Km/h）（限速120）': 200,
    '小型车超速（即时速度181 Km/h以上）（限速120）': 2000,
    '小型车超速（即时速度145-180<含>Km/h）（限速120）': 200,
    '小型车超速（即时速度133-150<含> Km/h）（限速80）': 500,
    '小型车超速（平均速度121-150<含>Km/h）（限速100）': 200,
    '小型车超速（平均速度105-132<含>Km/h）（限速100）': 200,
    '机动车在道路上发生故障或者发生交通事故，妨碍交通又难以移动的，未按规定开启危险报警闪光灯并在车后50至100米处设置警告标志': 200,
    '机动车行驶时，驾驶人未按规定使用安全带': 100,
    '在道路上行驶超过限速标志、标线标明的速度': 200,
    '非紧急情况时在应急车道停车': 200,
    '驾驶机动车违反禁令标志、禁止标线指示的': 200,
    '非紧急情况时在应急车道行驶': 200,
    '车辆未按照交通信号通行': 200,
    '驾驶机动车时有拨打接听手持电话、观看电视等妨碍安全驾驶的行为': 200,
    '机动车在道路上行驶超过限速标志、标线标明的速度，且超过规定时速百分之五十': 500,
    '在道路同方向划有2条以上机动车车道的情况下，驾驶机动车变更车道影响了相关车道内行驶的机动车的正常行驶': 200,
    '在实习期内不符合规定驾驶机动车': 200,
}


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
            vio_info.vio_point = 0
            vio_money = PUNISH_DIC.get(vio_info.vio_activity, 0)
            vio_info.vio_money = vio_money
            vio_info.vio_loc = '重庆高速'

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
            # print(raw_data.status_code)

            if raw_data.status_code == 200:
                vio_list = get_std_vio_data(raw_data.content.decode())
                vehicle.spider_status = 1
                vehicle.save()
                # print(vio_list)

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
    for i in range(100):
        t_query_thread = Thread(target=query_thread, args=(vehicle_queue,))
        t_query_thread.start()


if __name__ == '__main__':
    main()
