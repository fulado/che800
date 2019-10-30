import requests
import json
import pprint
import xlrd
import xlwt


def get_vio_for_wantong(v_number, v_type, e_code):

    url = 'http://api.haoyi.link/api/Sh_yangche'

    app_key = 'mW11sLBS2DIOVdSV'
    app_secret = 'JlvNdWPQuaTm8GfKJRVCSJ0lCfxdXGuo'

    data = {'appkey': app_key,
            'appsecret': app_secret,
            'cx': v_type,
            'cp': v_number,
            'fdj': e_code
            }

    response_data = requests.get(url, data)

    # pprint.pprint(json.loads(response_data.content.decode()))
    return json.loads(response_data.content.decode())


# 根据万通接口查询结果构造标准返回数据
def vio_dic_for_wantong(v_number, data):
    """
    通过典典接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 车轮接口返回数据, dict
    :return: 车八佰违章数据, dict
    """

    status_code = data.get('code', -1)

    if status_code == '200':

        vio_list = []

        for vio in data.get('data', ''):

            fine_status = vio.get('jfzt', '')  # 缴费状态

            if '未缴款' == fine_status:
                vio_pay = 0
            elif '已缴款' == fine_status:
                vio_pay = 1
            else:
                vio_pay = -1

            # 已经缴费的违章数据不再返回
            if vio_pay == 1:
                continue

            deal_status = vio.get('clzt', '')  # 处理状态
            # 处理状态
            if '未处理' in deal_status:
                vio_deal = 0
            elif '已处理' in deal_status:
                vio_deal = 1
            else:
                vio_deal = -1

            # 违法时间
            vio_time = vio.get('wfsj', '')
            vio_address = vio.get('wfdz', '')  # 违法地点
            vio_activity = vio.get('wfxw', '')  # 违法行为
            vio_point = vio.get('wfkf', '')  # 扣分
            vio_money = vio.get('fkje', '')  # 罚款
            vio_code = vio.get('wfdm', '')  # 违法代码
            vio_loc = vio.get('fxjgmc', '')  # 处理机关

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

        vio_dict = {'vehicleNumber': v_number, 'status': 0, 'data': vio_list}
    else:
        return get_status(data.get('status_code', -1), 8)

    return vio_dict


# 根据车务帮接口的返回状态码构造本地平台返回给用户的状态码
def create_status_from_wantong(origin_status):
    if origin_status == 1007:
        status = 36
        msg = '车辆信息不正确'
    elif origin_status == 500:
        status = 39
        msg = '数据源不稳定, 请稍后再查'
    else:
        status = 51
        msg = '数据源异常'

    return {'status': status, 'msg': msg}


# 根据不同接口的返回状态码构造本地平台返回给用户的状态码
def get_status(origin_status, url_id):

    # 车务帮接口
    if url_id == 9:
        return create_status_from_wantong(int(origin_status))
    else:
        return {'status': 51, 'msg': '数据源异常'}


def read_vehicle_info_from_file(filename):

    workbook = xlrd.open_workbook(filename)
    sheets = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(sheets[0])

    # 读取数据
    vehicle_list = []
    for i in range(1, worksheet.nrows):
        # 读取一条车辆信息
        # ctype： 0-empty, 1-string, 2-number, 3-date, 4-boolean, 5-error

        v_number = int(worksheet.cell_value(i, 0))
        v_type = int(worksheet.cell_value(i, 1))
        e_code = int(worksheet.cell_value(i, 2))

        vehicle_info = {
            'v_number': v_number,
            'v_type': v_type,
            'e_code': e_code
        }

        vehicle_list.append(vehicle_info)

    return vehicle_list


def write_vehicle_info_to_file(filename):

    # 创建工作簿
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sheet1', cell_overwrite_ok=True)

    # 设置表头
    title = ['车牌号码', '车辆类型', '办理单位']

    # 生成表头
    len_col = len(title)
    for i in range(0, len_col):
        ws.write(0, i, title[i])

    # 写入办结事项数据
    i = 1
    for item_info in item_list:

        # 生成excel内容: ['工单编号', '办理情况', '办理单位']
        content = [item_info.id, item_info.result, item_info.assign_dept.name]

        for j in range(0, len_col):
            ws.write(i, j, content[j])
        i += 1

        # # 修改是否已导出状态
        # item_info.is_exported = True
        # item_info.save()

    # 内存文件操作
    buf = io.BytesIO()

    # 将文件保存在内存中
    wb.save(buf)


def main():
    v_number = '沪J08105'
    v_type = '02'
    e_code = 'B6324S09040907225'

    vio_data = get_vio_for_wantong(v_number, v_type, e_code)

    vio_dict = vio_dic_for_wantong(v_number, vio_data)

    pprint.pprint(vio_dict)


if __name__ == '__main__':
    main()
