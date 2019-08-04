import hashlib, time, requests
import json
import pprint


def get_vio_from_cwb(v_number, v_type, vin):
    url = 'http://www.chewubang.net/api/get/fine/'

    username = "ChunBo"  # 用户名
    password = "XcJ6JeUIXMmP6bKzxigmNUuBvlVybMD2"  # 密码

    area = v_number[0] if v_number else ''
    timestamp = int(time.time())  # 当前时间10位unix时间戳

    sign = username + password + str(timestamp) + v_number + vin + v_type + area
    sign = hashlib.md5(sign.encode()).hexdigest()

    data = {  ##form表单数据
        "username": username,
        "brandType": v_type,
        "vehNumKey": vin,
        "time": timestamp,
        "carNum": v_number,
        "sign": sign,
        'area': area
    }

    response_data = requests.post(url=url, data=data)

    return json.loads(response_data.content.decode())


# 通过典典接口查询结果构造标准返回数据
def vio_dic_for_cwb(v_number, data):
    """
    通过典典接口查询结构构造标准返回数据
    :param v_number: 车牌
    :param data: 车轮接口返回数据, dict
    :return: 车八佰违章数据, dict
    """
    print(data)
    status_code = data.get('status_code', -1)

    if status_code == 2000:

        vio_list = []

        for vio in data.get('historys', ''):

            fine_status = vio.get('fine_status', '')  # 缴费状态

            if '未缴款' in fine_status:
                vio_pay = 0
            elif '已缴款' in fine_status:
                vio_pay = 1
            else:
                vio_pay = -1

            # 已经缴费的违章数据不再返回
            if vio_pay == 1:
                continue

            # 处理状态
            if '未处理' in fine_status:
                vio_deal = 0
            elif '已处理' in fine_status:
                vio_deal = 1
            else:
                vio_deal = -1

            # 违法时间
            vio_time = vio.get('occur_date', '')
            vio_address = vio.get('occur_area', '')  # 违法地点
            vio_activity = vio.get('info', '')  # 违法行为
            vio_point = vio.get('fen', '')  # 扣分
            vio_money = vio.get('money', '')  # 罚款
            vio_code = ''  # 违法代码
            vio_loc = ''  # 处理机关

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
def create_status_from_cwb(origin_status):
    if origin_status == 5000:
        status = 36
        msg = '车辆信息不正确'
    elif origin_status == 5003:
        status = 39
        msg = '数据源不稳定, 请稍后再查'
    else:
        status = 51
        msg = '数据源异常'

    return {'status': status, 'msg': msg}


# 根据不同接口的返回状态码构造本地平台返回给用户的状态码
def get_status(origin_status, url_id):

    # 车务帮接口
    if url_id == 8:
        return create_status_from_cwb(int(origin_status))
    else:
        return {'status': 51, 'msg': '数据源异常'}


# 车辆档案接口签名
def create_sign(hphm, hpzl, sf, syr):
    app_id = '100370'
    secret = '254c0cc463d0474c6e35b1994aa7f1dd'
    str_sign = 'appid=%s&hphm=%s&hpzl=%s&secret=%s&sf=%s&syr=%s' % (app_id, hphm, hpzl, secret, sf, syr)

    str_sign = hashlib.md5(str_sign.encode()).hexdigest()

    return str_sign


if __name__ == '__main__':
    # v_number = '闽DC3Q01'
    # v_type = '02'
    # vin = 'LSVNB4187HN044147'E3034066

    # v_number = '冀AC110Q'
    # v_type = '02'
    # vin = 'LJ166A330E7020540'
    #
    # vio_data = get_vio_from_cwb(v_number, v_type, vin)
    # pprint.pprint(vio_data)
    # vio_dic = vio_dic_for_cwb(v_number, vio_data)

    # pprint.pprint(vio_dic)

    hphm = 'DC76P1'
    hpzl = '02'
    sf = '浙'
    syr = '朱卫国'

    sign = create_sign(hphm, hpzl, sf, syr)

    print(sign)
