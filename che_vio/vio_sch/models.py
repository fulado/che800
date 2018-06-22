from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)  # 账号
    password = models.CharField(max_length=50, blank=False, null=False)               # 密码
    info = models.CharField(max_length=200, blank=True, null=True)                    # 用户信息
    authority = models.IntegerField(default=0)                                        # 权限: 0-企业, 1-管理员


class Type(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    type_name = models.CharField(max_length=20, blank=False, null=False, unique=True)  # 类型名称


class Location(models.Model):
    loc_name = models.CharField(max_length=20, blank=False, null=False, unique=True)  # 所在地名称


class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=20, blank=False, null=False, unique=True)  # 号牌号码
    engine_code = models.CharField(max_length=50, blank=True, null=True)                    # 发动机号
    vehicle_code = models.CharField(max_length=50, blank=True, null=True)                   # 车架号
    vehicle_type = models.ForeignKey(Type, on_delete=models.CASCADE, default=1, blank=False, null=False)   # 车辆类型
    status = models.IntegerField(default=1)                                        # 状态: 0-无效, 1-有效
    opt_loc = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, null=False)             # 运营地
    create_time = models.DateTimeField(blank=False, null=False)                 # 创建时间

