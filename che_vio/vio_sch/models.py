from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)    # 账号
    password = models.CharField(max_length=50, blank=False, null=False)                 # 密码
    info = models.CharField(max_length=200, blank=True, null=True)                      # 用户信息
    authority = models.IntegerField(default=0)                                          # 权限: 2-企业, 1-管理员
    is_valid = models.BooleanField(default=True)                                        # 是否可用
    timestamp = models.IntegerField(default=0, blank=False, null=False)                 # 时间戳
    number_limit = models.IntegerField(default=-1)
    number_used = models.IntegerField(default=0)


class VehicleType(models.Model):
    type_id = models.CharField(max_length=20, primary_key=True)
    type_name = models.CharField(max_length=20, blank=True, null=True)                 # 类型名称


class UrlInfo(models.Model):
    url_name = models.CharField(max_length=20, blank=True, null=True)                  # 接口名称


class LocInfo(models.Model):
    loc_id = models.CharField(max_length=20, primary_key=True)                                      # 城市代码
    loc_name = models.CharField(max_length=20, blank=True, null=True)                               # 城市名称
    plate_name = models.CharField(max_length=10, blank=True, null=True)                             # 车牌简称
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True, default=2)    # 查询接口url
    status = models.BooleanField(default=1)                                                         # 是否可以查询违章


class LocUrlRelation(models.Model):
    location = models.ForeignKey(LocInfo, on_delete=models.CASCADE, blank=True, null=True)  # 地区
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True)  # 接口
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)  # 用户


class VehicleInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)     # 号牌号码
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)        # 车辆类型
    vehicle_code = models.CharField(max_length=50, blank=True, null=True)       # 车架号
    engine_code = models.CharField(max_length=50, blank=True, null=True)        # 发动机号
    status = models.IntegerField(default=0)                                     # 状态: 0-失败, 1-成功
    spider_status = models.BooleanField(default=False)  # 爬虫状态: 0-未爬取数据, 1-已爬取重庆高速数据
    city = models.CharField(max_length=20, blank=True, null=True)               # 运营地
    update_time = models.DateTimeField(auto_now=True)                           # 更新时间
    query_counter = models.IntegerField(default=1)                              # 近7天查询违章次数
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)  # 所属用户


class VioInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)     # 号牌号码
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)        # 车辆类型
    vio_time = models.CharField(max_length=30, blank=True, null=True)           # 违法时间
    vio_position = models.CharField(max_length=100, blank=True, null=True)      # 违法地点
    vio_activity = models.CharField(max_length=255, blank=True, null=True)      # 违法行为
    vio_point = models.IntegerField(default=0, blank=True, null=True)           # 扣分
    vio_money = models.IntegerField(default=0, blank=True, null=True)           # 罚款
    vio_code = models.CharField(max_length=20, blank=True, null=True)           # 违法代码
    vio_loc = models.CharField(max_length=50, blank=True, null=True)            # 处理机关
    deal_status = models.IntegerField(default=-1, blank=True, null=True)    # 是否已处理, 0-否, 1-是, -1-未知
    pay_status = models.IntegerField(default=-1, blank=True, null=True)     # 是否已缴费, 0-否, 1-是, -1-未知


class LogInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)                     # 车牌号
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)                        # 车辆类型
    vehicle_code = models.CharField(max_length=50, blank=True, null=True)                       # 车架号
    engine_code = models.CharField(max_length=50, blank=True, null=True)                        # 发动机号
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)         # 所属用户
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True)           # 查询接口url
    query_time = models.DateTimeField(blank=True, null=True)                                    # 查询时间
    status = models.IntegerField(default=-1, blank=True, null=True)                             # 状态码
    msg = models.CharField(max_length=200, blank=True, null=True)                               # 备注信息
    ip = models.CharField(max_length=20, blank=True, null=True)                                 # ip地址
    city = models.CharField(max_length=20, blank=True, null=True)                               # 查询城市
    origin_status = models.IntegerField(default=0, blank=True, null=True)                       # 状态码
    origin_msg = models.CharField(max_length=200, blank=True, null=True)                        # 备注信息


class VehicleBackup(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)                 # 号牌号码
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)                    # 车辆类型
    vehicle_code = models.CharField(max_length=50, blank=True, null=True)                   # 车架号
    engine_code = models.CharField(max_length=50, blank=True, null=True)                    # 发动机号
    update_time = models.DateTimeField(auto_now=True)                                       # 更新时间


class VehicleInfoSz(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # 号牌号码
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)  # 车辆类型
    vehicle_code = models.CharField(max_length=50, blank=True, null=True)  # 车架号
    engine_code = models.CharField(max_length=50, blank=True, null=True)  # 发动机号
    status = models.IntegerField(default=99)  # 状态码: 99表示未查询，或未知问题导致的查询失败；0-查询成功
    msg = models.CharField(max_length=50, blank=True, null=True)  # 错误信息
    spider_status = models.BooleanField(default=False)  # 爬虫状态: 0-未爬取数据, 1-已爬取重庆高速数据
    city = models.CharField(max_length=20, blank=True, null=True)  # 运营地
    update_time = models.DateTimeField(auto_now=True)  # 更新时间
    query_counter = models.IntegerField(default=1)  # 近7天查询违章次数
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)  # 所属用户


class VioInfoSz(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)     # 号牌号码
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)        # 车辆类型
    vio_time = models.CharField(max_length=30, blank=True, null=True)           # 违法时间
    vio_position = models.CharField(max_length=100, blank=True, null=True)      # 违法地点
    vio_activity = models.CharField(max_length=100, blank=True, null=True)      # 违法行为
    vio_point = models.IntegerField(default=0, blank=True, null=True)           # 扣分
    vio_money = models.IntegerField(default=0, blank=True, null=True)           # 罚款
    vio_code = models.CharField(max_length=20, blank=True, null=True)           # 违法代码
    vio_loc = models.CharField(max_length=50, blank=True, null=True)            # 处理机关
    deal_status = models.IntegerField(default=-1, blank=True, null=True)    # 是否已处理, 0-否, 1-是, -1-未知
    pay_status = models.IntegerField(default=-1, blank=True, null=True)     # 是否已缴费, 0-否, 1-是, -1-未知


class VioCode(models.Model):
    vio_code = models.CharField(max_length=20, primary_key=True)            # 违法代码
    vio_activity = models.CharField(max_length=100, blank=True, null=True)  # 违法行为
    vio_point = models.IntegerField(default=0, blank=True, null=True)       # 扣分
    vio_money = models.IntegerField(default=0, blank=True, null=True)       # 罚款
