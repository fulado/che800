from django.db import models

# Create your models here.


# 用户表
class UserInfo(models.Model):
    username = models.CharField(max_length=50, unique=True)                     # 帐号
    password = models.CharField(max_length=50)                                  # 密码
    authority = models.IntegerField(default=1, null=True, blank=True)           # 权限等级, 1-企业权限, 2-管理员权限
    comments = models.CharField(max_length=200, null=True, blank=True)          # 企业名称
    is_delete = models.BooleanField(default=False)
    limitation = models.IntegerField(default=0, null=True, blank=True)          # 每日限制查询量
    queried_number = models.IntegerField(default=0, null=True, blank=True)      # 每日实际查询量


# 车辆表
class VehicleInfo(models.Model):
    number = models.CharField(max_length=20)                                # 号牌号码
    type = models.IntegerField(default=2, null=True, blank=True)            # 车辆类型, 2-小型车, 52-新能源小型车
    engine = models.CharField(max_length=50, null=True, blank=True)         # 发动机型号
    vin = models.CharField(max_length=50, null=True, blank=True)            # 车辆识别代码
    location = models.CharField(max_length=50, null=True, blank=True)       # 查询地
    status = models.IntegerField(default=-1, null=True, blank=True)         # 状态: -1-未查询, 0-无违章, n-有n条违章, -2-车辆信息不正确, -3-查询失败
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)  # 所属用户


# 违章表
class VioInfo(models.Model):
    number = models.CharField(max_length=20, blank=True, null=True)  # 号牌号码
    type = models.IntegerField(default=2, blank=True, null=True)  # 车辆类型
    time = models.CharField(max_length=30, blank=True, null=True)  # 违法时间
    position = models.CharField(max_length=100, blank=True, null=True)  # 违法地点
    activity = models.CharField(max_length=100, blank=True, null=True)  # 违法行为
    point = models.IntegerField(default=0, blank=True, null=True)  # 扣分
    money = models.IntegerField(default=0, blank=True, null=True)  # 罚款
    code = models.CharField(max_length=20, blank=True, null=True)  # 违法代码
    loc = models.CharField(max_length=50, blank=True, null=True)  # 处理机关
    deal_status = models.IntegerField(default=-1, blank=True, null=True)  # 是否已处理, 0-否, 1-是, -1-未知
    pay_status = models.IntegerField(default=-1, blank=True, null=True)  # 是否已缴费, 0-否, 1-是, -1-未知
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)  # 所属用户

