from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)  # 账号
    password = models.CharField(max_length=50, blank=False, null=False)               # 密码
    info = models.CharField(max_length=200, blank=True, null=True)                    # 用户信息
    authority = models.IntegerField(default=0)                                        # 权限: 0-企业, 1-管理员
    is_valid = models.BooleanField(default=1)                                         # 是否可用


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
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # 号牌号码
    engine_code = models.CharField(max_length=50, blank=True, null=True)                    # 发动机号
    vehicle_code = models.CharField(max_length=50, blank=True, null=True)                   # 车架号
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, default=1, blank=True, null=True)  # 车辆类型
    status = models.IntegerField(default=1)                                        # 状态: 0-无效, 1-有效
    opt_loc = models.ForeignKey(LocInfo, on_delete=models.CASCADE, blank=True, null=True)             # 运营地
    create_time = models.DateTimeField(blank=True, null=True)                 # 创建时间
    query_counter = models.IntegerField(default=0)                            # 查询违章次数

