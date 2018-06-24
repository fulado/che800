from django.db import models

# Create your models here.


# 用户信息表
class UserInfo(models.Model):
    username = models.CharField(max_length=50)                                  # 账号
    password = models.CharField(max_length=50)                                  # 密码
    valid_date = models.DateTimeField(default='2099-2-24 00:00:00')             # 帐号有效期
    full_name = models.CharField(max_length=50, null=True, blank=True)          # 名称全称


# ip白名单
class IpInfo(models.Model):
    ip_addr = models.CharField(max_length=50, unique=True)                     # ip地址
    user = models.ForeignKey(UserInfo, null=True, blank=True)                  # 所属用户


# 违法代码表
class VioCode(models.Model):
    code = models.CharField(max_length=10)                                  # 违法代码
    activity = models.CharField(max_length=200)  # 违法行为
    point = models.IntegerField(default=0)       # 扣分
    fine = models.IntegerField(default=0)        # 罚款金额
