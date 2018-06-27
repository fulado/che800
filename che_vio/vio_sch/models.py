from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)  # 账号
    password = models.CharField(max_length=50, blank=False, null=False)               # 密码
    info = models.CharField(max_length=200, blank=True, null=True)                    # 用户信息
    authority = models.IntegerField(default=0)                                        # 权限: 0-企业, 1-管理员
    is_valid = models.BooleanField(default=True)                                      # 是否可用


class VehicleType(models.Model):
    type_id = models.CharField(max_length=20, primary_key=True)
    type_name = models.CharField(max_length=20, blank=True, null=True)  # 类型名称


class UrlInfo(models.Model):
    url_name = models.CharField(max_length=20, blank=True, null=True)     # 接口名称


class LocInfo(models.Model):
    loc_id = models.CharField(max_length=20, primary_key=True)              # 城市代码
    loc_name = models.CharField(max_length=20, blank=True, null=True)       # 城市名称
    plate_name = models.CharField(max_length=10, blank=True, null=True)     # 车牌简称
    url_id = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True, default=2)  # 查询接口url
    status = models.BooleanField(default=1)         # 是否可以查询违章


class VehicleInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)     # 号牌号码
    vehicle_type = models.CharField(max_length=10, blank=True, null=True)       # 车辆类型
    vehicle_code = models.CharField(max_length=50, blank=True, null=True)       # 车架号
    engine_code = models.CharField(max_length=50, blank=True, null=True)        # 发动机号
    status = models.IntegerField(default=0)                                     # 状态: 0-无效, 1-有效, 如果车辆信息不正确, 则无效
    city = models.CharField(max_length=20, blank=True, null=True)               # 运营地
    create_time = models.DateTimeField(blank=True, null=True)                   # 创建时间
    query_counter = models.IntegerField(default=1)                              # 近7天查询违章次数


class VioInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)     # 号牌号码
    vehicle_type = models.CharField(max_length=10, blank=True, null=True)       # 车辆类型
    vio_time = models.DateTimeField(blank=True, null=True)                      # 违法时间
    vio_position = models.CharField(max_length=100, blank=True, null=True)      # 违法地点
    vio_activity = models.CharField(max_length=100, blank=True, null=True)      # 违法行为
    vio_point = models.IntegerField(default=0, blank=True, null=True)                                  # 扣分
    vio_money = models.IntegerField(default=0, blank=True, null=True)                                  # 罚款
    vio_code = models.CharField(max_length=20, blank=True, null=True)       # 违法代码
    vio_loc = models.CharField(max_length=50, blank=True, null=True)       # 处理机关


class LogInfo(models.Model):
    vehicle = models.ForeignKey(VehicleInfo, on_delete=models.CASCADE, blank=True, null=True)   # 车辆信息
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)         # 所属用户
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True)           # 查询接口url
    query_time = models.DateTimeField(blank=True, null=True)                                    # 查询时间
    status = models.IntegerField(default=-1, blank=True, null=True)                             # 状态码
    comments = models.CharField(max_length=200, blank=True, null=True)                          # 备注信

