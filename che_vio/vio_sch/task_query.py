import xlrd
import xlwt
import pprint
import time
import hashlib
import json
import requests

from .models import LocInfo


# 从懂云接口查询数据
def get_vio_from_doyun(v_number, v_type, v_code, e_code, city):
    """
    调用典典接口查询违章
    :param v_number: 车牌号
    :param v_type: 车辆类型
    :param v_code: 车架号
    :param e_code: 发动机号
    :return: 违章数据, json格式
    """
    # 查询接口url
    url = 'https://openapi.docloud.vip/violation/query/1.0'

    # 构造查询数据
    app_key = 'KSJWW7OABAMMV4VX'                        # 账号
    app_secret = 'YMPQFUKTTRIE4UA44NXN89SEEYCAIGQ7'     # 密码

    timestamp = int(time.time() * 1000)                 # 时间戳

    # 构造查询数据
    data = {'plateNumber': v_number, 'carType': v_type, 'engineNo': e_code, 'vin': v_code, 'city': city}
    data = json.dumps(data).replace(' ', '')

    # 构造sign
    sign = "%s%sapp_key=%s&timestamp=%d%s" % (app_key, app_secret, app_key, timestamp, data)
    sign = sign[::-1]
    sign = hashlib.md5(sign.encode('utf-8')).hexdigest().upper()

    # 构造完整查询url
    url = '%s?app_key=%s&timestamp=%d&sign=%s' % (url, app_key, timestamp, sign)

    # 请求头
    headers = {'Content-type': 'application/json'}

    # 创建request请求
    response_data = requests.post(url, headers=headers, data=data.encode('utf-8'), verify=False)

    return json.loads(response_data.content.decode())


# 通过典典接口查询结果构造标准返回数据
def vio_dic_for_ddyc(v_number, data):
    """
    通过典典接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 车轮接口返回数据, dict
    :return: 车八佰违章数据, dict
    """
    # print('vio_dic_for_ddyc')
    if 'success' in data and data['success']:
        status = 0

        vio_list = []
        if 'data' in data and 'violations' in data['data']:
            for vio in data['data']['violations']:
                # 缴费状态
                try:
                    if 'paymentStatus' in vio:
                        vio_pay = int(vio['paymentStatus'])
                    else:
                        vio_pay = -1
                except Exception as e:
                    print(e)
                    vio_pay = -1

                # 已经缴费的违章数据不再返回
                if vio_pay == 2:
                    continue

                # 违法时间
                if 'time' in vio:
                    vio_time = vio['time']
                else:
                    vio_time = ''

                # 违法地点
                if 'address' in vio:
                    vio_address = vio['address']
                else:
                    vio_address = ''

                # 违法行为
                if 'reason' in vio:
                    vio_activity = vio['reason']
                else:
                    vio_activity = ''

                # 扣分
                if 'point' in vio:
                    vio_point = str(vio['point'])
                else:
                    vio_point = ''

                # 罚款
                if 'fine' in vio:
                    vio_money = str(vio['fine'])
                else:
                    vio_money = ''

                # 违法代码
                if 'violationNum' in vio:
                    vio_code = vio['violationNum']
                else:
                    vio_code = ''

                # 处理机关
                vio_id = vio.get('violationWritNo', '')
                if vio_id != '':
                    vio_loc = get_loc_by_vio_id_doyun(vio_id)
                elif 'violationCity' in vio:
                    vio_loc = vio['violationCity']
                else:
                    vio_loc = ''

                # 处理状态
                try:
                    if 'processStatus' in vio:
                        vio_deal = int(vio['processStatus'])
                    else:
                        vio_deal = -1
                except Exception as e:
                    print(e)
                    vio_deal = -1

                if vio_deal == 3:
                    vio_deal = '1'
                elif vio_deal == -1:
                    vio_deal = '-1'
                else:
                    vio_deal = '0'

                if vio_pay == 2:
                    vio_pay = '1'
                elif vio_pay == -1:
                    vio_pay = '-1'
                else:
                    vio_pay = '0'

                vio_data = {
                    'time': vio_time,
                    'position': vio_address,
                    'activity': vio_activity,
                    'point': vio_point,
                    'money': vio_money,
                    'code': vio_code,
                    'location': vio_loc,
                    'deal': vio_deal,
                    'pay': vio_pay
                }

                vio_list.append(vio_data)

        vio_dict = {'vehicleNumber': v_number, 'status': status, 'data': vio_list}
    else:
        if 'errCode' in data:
            return {'status': 53, 'msg': '查询失败'}
        else:
            return {'status': 53, 'msg': '查询失败'}

    return vio_dict


# 通过懂云返回的违法文书号判断违法地点
def get_loc_by_vio_id_doyun(vio_id):

    if len(vio_id) < 4:
        return ''

    if vio_id[0: 2] in ['11', '12', '31', '50']:
        loc_id = vio_id[0: 2] + '0000'
    else:
        loc_id = vio_id[0: 4] + '00'

    try:
        loc_info = LocInfo.objects.get(loc_id=loc_id)
    except Exception as e:
        print(e)
        try:
            loc_id = vio_id[0: 2] + '0000'
            loc_info = LocInfo.objects.get(loc_id=loc_id)
            return loc_info.loc_name
        except Exception as e:
            print(e)
            return ''

    return loc_info.loc_name


def get_vehicle_info_form_file(file_name, vehicle_list):
    # 打开excel文件, 直接从内存读取文件内容
    workbook = xlrd.open_workbook(filename=file_name)
    # 获得sheets列表
    sheets = workbook.sheet_names()
    # 获得第一个sheet对象
    worksheet = workbook.sheet_by_name(sheets[0])
    # 遍历
    for i in range(1, worksheet.nrows):
        # 读取一条车辆信息

        vehicle_number = worksheet.cell_value(i, 0)
        e_code = worksheet.cell_value(i, 1)
        v_code = worksheet.cell_value(i, 2)

        vehicle_info = {'vehicle_number': vehicle_number,
                        'e_code': e_code,
                        'v_code': v_code,
                        }

        vehicle_list.append(vehicle_info)


def get_violations(vehicle_list, vio_list):
    for vehicle_info in vehicle_list:
        vio_data = get_vio_from_doyun(vehicle_info.get('vehicle_number'), '02', vehicle_info.get('e_code'),
                                      vehicle_info.get('v_code'), '')

        vio_dic = vio_dic_for_ddyc(vehicle_info.get('vehicle_number'), vio_data)

        vio_list.append(vio_dic)


def write_vio_info_to_file(vio_list):
    # 创建工作簿
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sheet1', cell_overwrite_ok=True)

    # 设置表头
    title = ['车牌号码', '违法时间', '违法地点', '违法行为', '扣分', '罚款金额', '违法代码',
             '处理机关', '是否处理', '是否缴费']

    # 生成表头
    len_col = len(title)
    for i in range(0, len_col):
        ws.write(0, i, title[i])

    # 写入车辆数据
    i = 1
    for vio_info in vio_list:
        vehicle_number = vio_info.get('vehicleNumber', '')

        vio_info_list = vio_info.get('data', '')
        if vio_info_list == '':
            break

        for vio in vio_info.get('data'):
            vio_time = vio.get('time')
            vio_postion = vio.get('position')
            vio_activity = vio.get('activity')
            vio_point = vio.get('point')
            vio_money = vio.get('money')
            vio_code = vio.get('code')
            vio_location = vio.get('location')
            vio_deal = vio.get('deal')
            vio_pay = vio.get('pay')

            # 生成excle内容: ['ID', 'HPHM', 'HPZL', 'WFDM', 'QSSJ', 'JZSJ']
            content = [vehicle_number, vio_time, vio_postion, vio_activity, vio_point, vio_money,
                       vio_code, vio_location, vio_deal, vio_pay]

            for j in range(0, len_col):
                ws.write(i, j, content[j])
            i += 1

    wb.save('/Users/Barry/02_work/08_车八百/vio_info.xls')


def main():
    file_name = '/Users/Barry/02_work/08_车八百/vehicle_info.xlsx'

    vehicle_list = []
    get_vehicle_info_form_file(file_name, vehicle_list)

    vio_list = []
    get_violations(vehicle_list, vio_list)

    write_vio_info_to_file(vio_list)

    print('ok')
    # pprint.pprint(vio_list)


if __name__ == '__main__':
    main()
