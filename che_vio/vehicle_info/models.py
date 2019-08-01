from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)    # 账号
    password = models.CharField(max_length=50, blank=False, null=False)                 # 密码
    info = models.CharField(max_length=200, blank=True, null=True)                      # 用户信息
    authority = models.IntegerField(default=0)                                          # 权限: 2-企业, 1-管理员
    is_valid = models.BooleanField(default=True)                                        # 是否可用
    permit_province = models.CharField(max_length=300, blank=True, null=True)           # 时间戳


class UrlInfo(models.Model):
    url_name = models.CharField(max_length=20, blank=True, null=True)                  # 接口名称


class LogInfo(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)         # 所属用户
    ip = models.CharField(max_length=20, blank=True, null=True)                                 # ip地址
    query_time = models.DateTimeField(blank=True, null=True)                                    # 查询时间
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)                     # 车牌号
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)                        # 车辆类型
    vehicle_owner = models.CharField(max_length=500, blank=True, null=True)                     # 所有人
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True)           # 查询接口url
    status = models.IntegerField(default=-1, blank=True, null=True)                             # 状态码
    msg = models.CharField(max_length=200, blank=True, null=True)                               # 备注信息
    origin_status = models.IntegerField(default=0, blank=True, null=True)                       # 状态码
    origin_msg = models.CharField(max_length=200, blank=True, null=True)                        # 备注信息


class VehicleInfo(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # 车牌号
    vehicle_type = models.IntegerField(default=2, blank=True, null=True)  # 车辆类型
    vehicle_owner = models.CharField(max_length=500, blank=True, null=True)  # 所有人

