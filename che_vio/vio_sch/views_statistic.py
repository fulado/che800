"""
查询次数统计
"""

import pymysql
import calendar
import xlwt


def monthly_times_query(year, month, vehicle_dic):
    # 日期信息
    end_day = calendar.monthrange(int(year), int(month))[1]

    for day in range(1, end_day + 1):
        if day < 10:
            day = '%s%s0%d' % (year, month, day)
        else:
            day = '%s%s%d' % (year, month, day)

        print(day)
        day_times_query(day, vehicle_dic)


def day_times_query(day, vehicle_dic):
    # 数据库连接信息
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

        # 神州租车
        # sql = 'SELECT DISTINCT vehicle_number, status from vio_sch_loginfo_%s ' \
        #       'where user_id=6 and url_id not in (98, 100) and status<>51 ' % day

        # 神州买卖车
        # sql = 'SELECT DISTINCT vehicle_number, status from vio_sch_loginfo_%s ' \
        #       'where user_id=15 and url_id not in (98, 100) and status not in (97, 41, 39)' % day

        # 懂云查询统计
        # sql = 'SELECT vehicle_number, status from vio_sch_loginfo_%s ' \
        #       'where url_id = 7 and status not in (97, 41, 39, 51, 31)' % day

        # 盔甲查询统计
        sql = 'SELECT vehicle_number, status from vio_sch_loginfo_%s ' \
              'where user_id = 3' % day

        # 上海查询统计
        # sql = 'SELECT id FROM `vio_sch_loginfo_%s` where url_id=6 and status not in (51, 39, 41, 31)' % day

        # 上海接口查询统计

        cs.execute(sql)
        results = cs.fetchall()

        vehicle_dic[day] = len(results)

        # for r in results:
        #     vehicle = r[0]
        #     # 神州统计
        #     save_vehicle_into_dic(vehicle, vehicle_dic)
        #     # save_vehicle_into_dic_by_location(vehicle, vehicle_dic)

    except Exception as e:
        print(e)

    finally:
        # 关闭Cursor
        cs.close()

        # 关闭连接
        conn.close()


def save_vehicle_into_dic(vehicle, vehicle_dic):

    for k in vehicle_dic:
        if vehicle == k:
            vehicle_dic[k] += 1
            return

    vehicle_dic[vehicle] = 1


def save_vehicle_into_dic_by_location(vehicle, vehicle_dic):

    for k in vehicle_dic:
        if vehicle[0] == k:
            vehicle_dic[k] += 1
            return

    vehicle_dic[vehicle[0]] = 1


def export_excel(vehicle_dic, month):
    # 创建工作簿
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sheet1', cell_overwrite_ok=True)

    # 设置表头
    title = ['车牌号码', '查询次数']

    # 生成表头
    len_col = len(title)
    for i in range(0, len_col):
        ws.write(0, i, title[i])

    # 写入车辆数据
    i = 1
    for key in vehicle_dic:
        # 读取违章数据

        content = [key,
                   v_dic[key]
                   ]

        for j in range(0, len_col):
            ws.write(i, j, content[j])
        i += 1

    # 将文件保存在内存中
    wb.save(r'D:\2019%s.xls' % month)


if __name__ == '__main__':
    v_dic = {}
    query_year = '2019'

    # monthly_times_query(query_year, query_month, v_dic)
    #
    # export_excel(v_dic, query_month)

    month_list = ['06']

    for query_month in month_list:
        v_dic = {}
        monthly_times_query(query_year, query_month, v_dic)
        export_excel(v_dic, query_month)

