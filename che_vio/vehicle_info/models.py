from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)    # 账号
    password = models.CharField(max_length=50, blank=False, null=False)                 # 密码
    info = models.CharField(max_length=200, blank=True, null=True)                      # 用户信息
    authority = models.IntegerField(default=0)                                          # 权限: 2-企业, 1-管理员
    is_valid = models.BooleanField(default=True)                                        # 是否可用
    permit_province = models.CharField(max_length=300, blank=True, null=True)           # 时间戳
