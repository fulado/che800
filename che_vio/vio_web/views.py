from django.shortcuts import render
import time
import pymysql

# Create your views here.


def shenzhou(request):
    query_time = request.GET.get('query_time', time.strftime('%Y-%m-%d', time.localtime()))

    # host = '172.21.0.2'
    host = '127.0.0.1'
    password = 'Init1234'
    port = 3306
    user = 'root'
    database = 'violation'
    charset = 'utf8mb4'

    try:
        # 创建连接
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

        # 获取Cursor对象
        cs = conn.cursor()

        # 查询表名
        table_name = 'vio_sch_loginfo_%s' % query_time.replace('-', '')
        # sql语句
        sql = 'select count(*) from %s where vehicle_number in (' \
              'select vehicle_nu mber from %s where user_id=6 and status=0) ' \
              'and vio_code<>999999;' % (table_name, table_name)

        count = cs.execute(sql)

        print(count)
    except Exception as e:
        print(e)

    # finally:
        # # 关闭Cursor
        # cs.close()
        #
        # # 关闭连接
        # conn.close()

    return render(request, 'shenzhou.html')
