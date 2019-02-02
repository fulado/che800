import pymongo


# 获得MongoDB数据库连接
def get_db():
    try:
        # mongodb数据库ip, 端口
        mongodb_ip = '192.168.100.234'
        mongodb_port = 27017

        # 创建连接对象
        client = pymongo.MongoClient(host=mongodb_ip, port=mongodb_port)

        # 获得数据库
        vio_db = client.violation

        return vio_db
    except Exception as e:
        print(e)
        raise e

