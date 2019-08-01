from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)    # 账号
    password = models.CharField(max_length=50, blank=False, null=False)                 # 密码
    info = models.CharField(max_length=200, blank=True, null=True)                      # 用户信息
    authority = models.IntegerField(default=0)                                          # 权限: 2-企业, 1-管理员
    is_valid = models.BooleanField(default=True)                                        # 是否可用
    permit_province = models.CharField(max_length=300, blank=True, null=True)           # 允许查询地区
    number_limit = models.IntegerField(default=0)
    number_used = models.IntegerField(default=0)


class UrlInfo(models.Model):
    url_name = models.CharField(max_length=20, blank=True, null=True)                  # 接口名称


class LogInfo(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)         # 所属用户
    ip = models.CharField(max_length=20, blank=True, null=True)                                 # ip地址
    query_time = models.DateTimeField(blank=True, null=True)                                    # 查询时间
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)                     # 车牌号
    vehicle_type = models.CharField(max_length=10, blank=True, null=True)                       # 车辆类型
    vehicle_owner = models.CharField(max_length=500, blank=True, null=True)                     # 所有人
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True)           # 查询接口url
    status = models.IntegerField(default=-1, blank=True, null=True)                             # 状态码
    msg = models.CharField(max_length=200, blank=True, null=True)                               # 备注信息
    src_status = models.IntegerField(default=0, blank=True, null=True)                          # 状态码
    src_msg = models.CharField(max_length=200, blank=True, null=True)                           # 备注信息


class VehicleInfo(models.Model):
    hphm = models.CharField(max_length=30, blank=True, null=True)  # 号牌号码
    hpzl = models.CharField(max_length=30, blank=True, null=True)  # 号牌种类
    syr = models.CharField(max_length=500, blank=True, null=True)  # 机动车所有⼈
    clpp1 = models.CharField(max_length=100, blank=True, null=True)  # 中文品
    clxh = models.CharField(max_length=100, blank=True, null=True)  # 车辆型号
    clsbdh = models.CharField(max_length=30, blank=True, null=True)  # 车辆识别代号
    fdjh = models.CharField(max_length=30, blank=True, null=True)  # 发动机号
    cllx = models.CharField(max_length=30, blank=True, null=True)  # 车辆类型
    csys = models.CharField(max_length=30, blank=True, null=True)  # 车身颜色
    syxz = models.CharField(max_length=30, blank=True, null=True)  # 使用性质
    ccdjrq = models.CharField(max_length=30, blank=True, null=True)  # 初次登记日期
    yxqz = models.CharField(max_length=30, blank=True, null=True)  # 检验有有效期止
    qzbfqz = models.CharField(max_length=30, blank=True, null=True)  # 强制报废期止
    zt = models.CharField(max_length=30, blank=True, null=True)  # 机动车状态
    fdjxh = models.CharField(max_length=50, blank=True, null=True)  # 发动机型号
    rlzl = models.CharField(max_length=30, blank=True, null=True)  # 燃料料种类
    pl = models.CharField(max_length=30, blank=True, null=True)  # 排量
    gl = models.CharField(max_length=30, blank=True, null=True)  # 功率
    zs = models.CharField(max_length=30, blank=True, null=True)  # 轴数
    zj = models.CharField(max_length=30, blank=True, null=True)  # 轴距
    qlj = models.CharField(max_length=30, blank=True, null=True)  # 前轮距
    hlj = models.CharField(max_length=30, blank=True, null=True)  # 后轮距
    zzl = models.CharField(max_length=30, blank=True, null=True)  # 总质量
    zbzl = models.CharField(max_length=30, blank=True, null=True)  # 整备质量
    hdzzl = models.CharField(max_length=30, blank=True, null=True)  # 核定载质量
    hdzk = models.CharField(max_length=30, blank=True, null=True)  # 核定载客
    ccrq = models.CharField(max_length=30, blank=True, null=True)  # 出厂日期


# class VehicleInfo(models.Model):
#     vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # 车牌号
#     vehicle_type = models.IntegerField(default=2, blank=True, null=True)  # 车辆类型
#     vehicle_owner = models.CharField(max_length=500, blank=True, null=True)  # 所有人
