import urllib.request
import base64
import json
import xlwt
import pymysql


def get_response_encoded_data(url, data):
    # base64加密
    data = base64.b64encode(data.encode('utf-8'))
    data = 'param=%s' % data.decode('utf-8')
    # print(data)

    request = urllib.request.Request(url, data.encode('utf-8'))

    response = urllib.request.urlopen(request)

    return base64.b64decode(response.read())


def get_json(data):
    data = data.decode('utf-8')
    return json.loads(data)


def get_token():
    data = str({"username": 'my_test', 'password': 'my_test'})
    url = 'http://111.160.75.92:9528/violation-point/login'

    data = get_json(get_response_encoded_data(url, data))

    return data['token']


def get_violation(car_list):
    url = 'http://111.160.75.92:9528/violation-point/illgledata/vehicleDate'

    token = get_token()
    data = json.dumps({'userId': 'my_test', 'token': token, 'cars': car_list})

    data = get_response_encoded_data(url, data)

    return get_json(data)


def save_to_excel(vio_list):
    # 创建工作簿
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sheet1', cell_overwrite_ok=True)

    # 设置表头
    title = ['车牌号码', '违法时间', '违法地点', '违法行为', '处理机构']

    # 生成表头
    len_col = len(title)
    for i in range(0, len_col):
        ws.write(0, i, title[i])

    # 写入车辆数据
    i = 1
    for vio in vio_list:
        for detail in vio['punishs']:
            ws.write(i, 0, vio['platNumber'])
            ws.write(i, 1, detail['time'])
            ws.write(i, 2, detail['location'])
            ws.write(i, 3, detail['reason'])
            ws.write(i, 4, detail['state'])
        i += 1

    # 将文件保存在内存中
    wb.save(r'D:\tianjin_vio.xls')


def get_vehicle_from_db(v_number):
    host = 'bj-cdb-gq8xi5ya.sql.tencentcdb.com'
    password = 'Init1234'
    port = 63226
    user = 'root'
    database = 'violation'
    charset = 'utf8mb4'

    try:
        # 创建连接
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

        # 获取Cursor对象
        cs = conn.cursor()

        # 日志表改名
        sql = 'SELECT vehicle_code, engine_code FROM `vio_sch_vehicleinfo` where vehicle_number="%s";' % v_number
        cs.execute(sql)

        data = cs.fetchone()

        vehicle_info = {
            'platNumber': v_number,
            'engineNumber': data[1],
            'vinNumber': data[0],
            'carType': '02'
        }

    except Exception as e:
        print(e)

    return vehicle_info


if __name__ == '__main__':

    violation_list = []
    car_list = [
        '津AZP198',
        '津RDK886',
        '津RBY613',
        '津AYG320',
        '津RMV918',
        '津AYG113',
        '津ASB685',
        '津RBC231',
        '津AUS352',
        '津LAX869',
        '津RCC905',
        '津RXL832',
        '津ASN315',
        '津RCF034',
        '津RTB339',
        '津RBN281',
        '津AZC640',
        '津AYQ551',
        '津AZP189',
        '津LAZ128',
        '津LAZ306',
        '津RCQ099',
        '津RTC000',
        '津AYG040',
        '津RBQ722',
        '津AYG193',
        '津AYG157',
        '津AYG040',
        '津LAZ158',
        '津RBS037',
        '津RGA109',
        '津LAZ322',
        '津AYG031',
        '津LAX859',
        '津RCB671',
        '津RUC113',
        '津AZP201',
        '津RHU289',
        '津AUS631',
        '津AYQ520',
        '津RHU289',
        '津LAX813',
        '津RDK284',
        '津RJA978',
        '津LAF106',
        '津RUL818',
        '津RTR110',
        '津RCH017',
        '津RFR129',
        '津AYQ005',
        '津RCH017',
        '津RKX338',
        '津LAX875',
        '津RYH282',
        '津AYG227',
        '津RCU060',
        '津RT7899',
        '津RGG583',
        '津RWR993',
        '津RUS712',
        '津RHA655',
        '津RBV352',
        '津RDQ808',
        '津RPD925',
        '津LAX875',
        '津LAZ311',
        '津RGL023',
        '津ASB970',
        '津AYG103',
        '津RCN109',
        '津RYP889',
        '津AZP031',
        '津RT7738',
        '津RS7493',

        '津APV665',
        '津RT7879',
        '津AYG103',

        '津AXT270',
        '津LAX950',
        '津REB106',
        '津AZP210',
        '津LAZ159',
        '津RDU031',
        '津RLE069',
        '津AZP210',
        '津LAF976',
        '津RMX170',
        '津RKJ291',
        '津RKF874',
        '津ASB787',
        '津RJB722',
        '津RHM087',
        '津RHA318',
        '津ASN061',
        '津RBA031',
        '津LAX878',
        '津AXT019',
        '津AYB325',
        '津RWC923',
        '津RHU208',
        '津LAZ211',
        '津LAZ211',
        '津RLQ658',
        '津RCC040',
        '津RCG484',
        '津ASB951',
        '津RWM601',
        '津RKU133',
        '津LAX830',
        '津LAZ069'
    ]

    for car_number in car_list:
        car_info = get_vehicle_from_db(car_number)
        cars = []
        cars.append(car_info)

        violation_data = get_violation(cars).get('result', '')

        violation_data = violation_data[0]

        if len(violation_data.get('punishs')) > 0:
            violation_list.append(violation_data)

    save_to_excel(violation_list)
