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
    vin = models.CharField(max_length=30, blank=True, null=True)                                # 车架号
    url = models.ForeignKey(UrlInfo, on_delete=models.CASCADE, blank=True, null=True)           # 查询接口url
    status = models.IntegerField(default=-1, blank=True, null=True)                             # 状态码
    msg = models.CharField(max_length=200, blank=True, null=True)                               # 备注信息
    src_status = models.IntegerField(default=0, blank=True, null=True)                          # 状态码
    src_msg = models.CharField(max_length=200, blank=True, null=True)                           # 备注信息


class VehicleInfo(models.Model):
    # hphm = models.CharField(max_length=30, blank=True, null=True)  # 号牌号码
    # hpzl = models.CharField(max_length=30, blank=True, null=True)  # 号牌种类
    # syr = models.CharField(max_length=500, blank=True, null=True)  # 机动车所有⼈
    # clpp1 = models.CharField(max_length=100, blank=True, null=True)  # 中文品
    # clxh = models.CharField(max_length=100, blank=True, null=True)  # 车辆型号
    # clsbdh = models.CharField(max_length=30, blank=True, null=True)  # 车辆识别代号
    # fdjh = models.CharField(max_length=30, blank=True, null=True)  # 发动机号
    # cllx = models.CharField(max_length=30, blank=True, null=True)  # 车辆类型
    # csys = models.CharField(max_length=30, blank=True, null=True)  # 车身颜色
    # syxz = models.CharField(max_length=30, blank=True, null=True)  # 使用性质
    # ccdjrq = models.CharField(max_length=30, blank=True, null=True)  # 初次登记日期
    # yxqz = models.CharField(max_length=30, blank=True, null=True)  # 检验有有效期止
    # qzbfqz = models.CharField(max_length=30, blank=True, null=True)  # 强制报废期止
    # zt = models.CharField(max_length=30, blank=True, null=True)  # 机动车状态
    # fdjxh = models.CharField(max_length=50, blank=True, null=True)  # 发动机型号
    # rlzl = models.CharField(max_length=30, blank=True, null=True)  # 燃料料种类
    # pl = models.CharField(max_length=30, blank=True, null=True)  # 排量
    # gl = models.CharField(max_length=30, blank=True, null=True)  # 功率
    # zs = models.CharField(max_length=30, blank=True, null=True)  # 轴数
    # zj = models.CharField(max_length=30, blank=True, null=True)  # 轴距
    # qlj = models.CharField(max_length=30, blank=True, null=True)  # 前轮距
    # hlj = models.CharField(max_length=30, blank=True, null=True)  # 后轮距
    # zzl = models.CharField(max_length=30, blank=True, null=True)  # 总质量
    # zbzl = models.CharField(max_length=30, blank=True, null=True)  # 整备质量
    # hdzzl = models.CharField(max_length=30, blank=True, null=True)  # 核定载质量
    # hdzk = models.CharField(max_length=30, blank=True, null=True)  # 核定载客
    # ccrq = models.CharField(max_length=30, blank=True, null=True)  # 出厂日期

    xh = models.CharField(max_length=15, blank=True, null=True)  # 机动车序号
    hpzl = models.CharField(max_length=2, blank=True, null=True)  # 号牌种类
    hphm = models.CharField(max_length=15, blank=True, null=True)  # 号牌号码
    clpp1 = models.CharField(max_length=35, blank=True, null=True)  # 中文品牌
    clxh = models.CharField(max_length=35, blank=True, null=True)  # 车辆型号
    clpp2 = models.CharField(max_length=35, blank=True, null=True)  # 英文品牌
    gcjk = models.CharField(max_length=1, blank=True, null=True)  # 国产/进口
    zzg = models.CharField(max_length=3, blank=True, null=True)  # 制造国
    zzcmc = models.CharField(max_length=65, blank=True, null=True)  # 制造厂名称
    clsbdh = models.CharField(max_length=25, blank=True, null=True)  # 车辆识别代号
    fdjh = models.CharField(max_length=30, blank=True, null=True)  # 发动机号
    cllx = models.CharField(max_length=3, blank=True, null=True)  # 车辆类型
    csys = models.CharField(max_length=5, blank=True, null=True)  # 车身颜色
    syxz = models.CharField(max_length=1, blank=True, null=True)  # 使用性质
    syr = models.CharField(max_length=128, blank=True, null=True)  # 机动车所有人
    ccdjrq = models.CharField(max_length=30, blank=True, null=True)  # 初次登记日期
    djrq = models.CharField(max_length=30, blank=True, null=True)  # 最近定检日期
    yxqz = models.CharField(max_length=30, blank=True, null=True)  # 检验有效期止
    qzbfqz = models.CharField(max_length=30, blank=True, null=True)  # 强制报废期止
    fzjg = models.CharField(max_length=10, blank=True, null=True)  # 发证机关
    glbm = models.CharField(max_length=150, blank=True, null=True)  # 管理部门
    bxzzrq = models.CharField(max_length=30, blank=True, null=True)  # 保险终止日期
    zt = models.CharField(max_length=10, blank=True, null=True)  # 机动车状态
    dybj = models.CharField(max_length=1, blank=True, null=True)  # 抵押标记, 0-未抵押, 1-已抵押
    fdjxh = models.CharField(max_length=65, blank=True, null=True)  # 发动机型号
    rlzl = models.CharField(max_length=5, blank=True, null=True)  # 燃料种类
    pl = models.CharField(max_length=30, blank=True, null=True)  # 排量
    gl = models.CharField(max_length=30, blank=True, null=True)  # 功率
    zxxs = models.CharField(max_length=1, blank=True, null=True)  # 转向形式
    cwkc = models.CharField(max_length=30, blank=True, null=True)  # 车外廓长
    cwkk = models.CharField(max_length=30, blank=True, null=True)  # 车外廓宽
    cwkg = models.CharField(max_length=30, blank=True, null=True)  # 车外廓高
    hxnbcd = models.CharField(max_length=30, blank=True, null=True)  # 货箱内部长度
    hxnbkd = models.CharField(max_length=30, blank=True, null=True)  # 货箱内部宽度
    hxnbgd = models.CharField(max_length=30, blank=True, null=True)  # 货箱内部高度
    gbthps = models.CharField(max_length=30, blank=True, null=True)  # 钢板弹簧片数
    zs = models.CharField(max_length=30, blank=True, null=True)  # 轴数
    zj = models.CharField(max_length=30, blank=True, null=True)  # 轴距
    qlj = models.CharField(max_length=30, blank=True, null=True)  # 前轮距
    hlj = models.CharField(max_length=30, blank=True, null=True)  # 后轮距
    ltgg = models.CharField(max_length=65, blank=True, null=True)  # 轮胎规格
    lts = models.CharField(max_length=30, blank=True, null=True)  # 轮胎数
    zzl = models.CharField(max_length=30, blank=True, null=True)  # 总质量
    zbzl = models.CharField(max_length=30, blank=True, null=True)  # 整备质量
    hdzzl = models.CharField(max_length=30, blank=True, null=True)  # 核定载质量
    hdzk = models.CharField(max_length=30, blank=True, null=True)  # 核定载客
    zqyzl = models.CharField(max_length=30, blank=True, null=True)  # 准牵引总质量
    qpzk = models.CharField(max_length=30, blank=True, null=True)  # 驾驶室前排载客人数
    hpzk = models.CharField(max_length=30, blank=True, null=True)  # 驾驶室后排载客人数
    hbdbqk = models.CharField(max_length=130, blank=True, null=True)  # 环保达标情况
    ccrq = models.CharField(max_length=30, blank=True, null=True)  # 出厂日期
    clyt = models.CharField(max_length=2, blank=True, null=True)  # 车辆用途
    ytsx = models.CharField(max_length=1, blank=True, null=True)  # 用途属性
    xszbh = models.CharField(max_length=30, blank=True, null=True)  # 行驶证证芯编号
    jyhgbzbh = models.CharField(max_length=30, blank=True, null=True)  # 检验合格标志
    xzqh = models.CharField(max_length=30, blank=True, null=True)  # 管理辖区
    zsxzqh = models.CharField(max_length=30, blank=True, null=True)  # 住所地址行政区划
    zzxzqh = models.CharField(max_length=30, blank=True, null=True)  # 联系地址行政区划
    sgcssbwqk = models.CharField(max_length=4000, blank=True, null=True)  # 事故车损伤部位情况
    sfmj = models.CharField(max_length=1, blank=True, null=True)  # 是否免检, 1-免检, 2-不免检
    bmjyy = models.CharField(max_length=4000, blank=True, null=True)  # 不免检原因
    sfxny = models.CharField(max_length=1, blank=True, null=True)  # 是否新能源汽车, 1-是, 2-否
    xnyzl = models.CharField(max_length=1, blank=True, null=True)  # 新能源汽车种类, A-纯电动, B-燃料电池, C-插电式混合动力
    bz = models.CharField(max_length=4000, blank=True, null=True)  # 备注


# class VehicleInfo(models.Model):
#     vehicle_number = models.CharField(max_length=20, blank=True, null=True)  # 车牌号
#     vehicle_type = models.IntegerField(default=2, blank=True, null=True)  # 车辆类型
#     vehicle_owner = models.CharField(max_length=500, blank=True, null=True)  # 所有人
