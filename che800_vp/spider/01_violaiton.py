import json
import requests
import pymysql
from pprint import pprint


CITY_DIC = {'青': 'qinghai',
            '云': 'yunnan',
            '甘': 'gansu',
            '赣': 'jiangxi',
            '皖': 'anhui',
            '晋': 'shanxi',
            '桂': 'guangxi',
            '宁': 'ningxia',
            '吉': 'jilin',
            '黑': 'heilongjiang',
            '辽': 'liaoning'
            }


# 查询违章
def query_vio_data(city, v_number, v_type, v_code, e_code):
    url = 'https://sp0.baidu.com/5LMDcjW6BwF3otqbppnN2DJv/traffic.pae.baidu.com/data/query'

    params = {
        'city': city,
        'hphm': v_number,
        'hpzl': v_type,
        'engine': e_code,
        'body': v_code,
        'source': 'pc'
    }

    response_data = requests.get(url=url, params=params)

    return response_data


# 将返回结果解码, 并保存到文件
def save_data_to_file(response_data, v_number):
    vio_data = response_data.content.decode('unicode_escape')

    f = open('vio_data.txt', 'a')
    f.write('%s : ' % v_number)
    f.write(vio_data)
    f.write('\r\n')

    f.close()


# 从数据库读取车辆信息
def get_vehicle_info():

    # 数据库连接信息
    host = '127.0.0.1'
    password = 'xiaobai'
    port = 3306
    user = 'root'
    database = 'violation'
    charset = 'utf8mb4'

    try:
        # 创建连接
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

        # 获取Cursor对象
        cs = conn.cursor()

        # 查询语句
        sql = """select vehicle_number, vehicle_type, vehicle_code, engine_code from vio_sch_vehicleinfo 
                                                         where vehicle_number like '青%' or
                                                               vehicle_number like '云%' or
                                                               vehicle_number like '甘%' or
                                                               vehicle_number like '赣%' or
                                                               vehicle_number like '皖%' or
                                                               vehicle_number like '晋%' or
                                                               vehicle_number like '桂%' or
                                                               vehicle_number like '宁%' or
                                                               vehicle_number like '吉%' or
                                                               vehicle_number like '黑%' or
                                                               vehicle_number like '辽%' limit 100;
                                                               """
        count = cs.execute(sql)

        for i in range(count):
            result = cs.fetchone()
            print(result)
            response_data = query_vio_data(CITY_DIC.get(result[0][0], ''), result[0], result[1], result[2], result[3])
            print(response_data.status_code)

            if int(response_data.status_code) == 200:
                save_data_to_file(response_data, result[0])

    except Exception as e:
        print(e)

    finally:
        cs.close()
        conn.close()


def main():
    # city = 'qinghai'
    # v_number = '青AXX435'
    # v_type = '02'
    # e_code = '5V1067'
    # v_code = '090071'
    #
    # response_data = query_vio_data(city, v_number, v_type, v_code, e_code)
    # print(response_data.status_code)
    #
    # if int(response_data.status_code) == 200:
    #     save_data_to_file(response_data)

    get_vehicle_info()


if __name__ == '__main__':
    main()
