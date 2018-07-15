from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)  # 账号
    password = models.CharField(max_length=50, blank=False, null=False)               # 密码
    info = models.CharField(max_length=200, blank=True, null=True)                    # 用户信息
    authority = models.IntegerField(default=0)                                        # 权限: 0-企业, 1-管理员
    is_valid = models.BooleanField(default=True)                                      # 是否可用
    timestamp = models.IntegerField(default=0, blank=False, null=False)                            # 时间戳


class VehicleType(models.Model):
    type_id = models.CharField(max_length=20, primary_key=True)
    type_name = models.CharField(max_length=20, blank=True, null=True)  # 类型名称


class UrlInfo(models.Model):
    url_name = models.CharField(max_length=20, blank=True, null=True)     # 接口名称


class LocInfo(models.Model):
    loc_id = models.CharField(max_length=20, primary_key=True)              # 城市代码
    loc_name = models.CharField(max_length=20, blank=True, null=True)       # 城市名称
    plate_name = models.CharField(max_length=10, blank=True, null=True)     # 车牌简称
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True, default=2)  # 查询接口url
    status = models.BooleanField(default=1)         # 是否可以查询违章


class VehicleInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)     # 号牌号码
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)        # 车辆类型
    vehicle_code = models.CharField(max_length=50, blank=True, null=True)       # 车架号
    engine_code = models.CharField(max_length=50, blank=True, null=True)        # 发动机号
    status = models.IntegerField(default=0)                                     # 状态: 0-失败, 1-成功
    city = models.CharField(max_length=20, blank=True, null=True)               # 运营地
    create_time = models.DateTimeField(blank=True, null=True)                   # 创建时间
    query_counter = models.IntegerField(default=1)                              # 近7天查询违章次数


class VioInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)     # 号牌号码
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)        # 车辆类型
    vio_time = models.CharField(max_length=30, blank=True, null=True)                     # 违法时间
    vio_position = models.CharField(max_length=100, blank=True, null=True)      # 违法地点
    vio_activity = models.CharField(max_length=100, blank=True, null=True)      # 违法行为
    vio_point = models.IntegerField(default=0, blank=True, null=True)                                  # 扣分
    vio_money = models.IntegerField(default=0, blank=True, null=True)                                  # 罚款
    vio_code = models.CharField(max_length=20, blank=True, null=True)       # 违法代码
    vio_loc = models.CharField(max_length=50, blank=True, null=True)       # 处理机关


class LogInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)                     # 车牌号
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)         # 所属用户
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True)           # 查询接口url
    query_time = models.DateTimeField(blank=True, null=True)                                    # 查询时间
    status = models.IntegerField(default=-1, blank=True, null=True)                             # 状态码
    msg = models.CharField(max_length=200, blank=True, null=True)                               # 备注信息
    ip = models.CharField(max_length=20, blank=True, null=True)                                 # ip地址
    city = models.CharField(max_length=20, blank=True, null=True)                               # 查询城市
    origin_status = models.IntegerField(default=0, blank=True, null=True)                       # 状态码
    origin_msg = models.CharField(max_length=200, blank=True, null=True)                        # 备注信息
