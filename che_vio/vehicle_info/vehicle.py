"""
车辆类
"""


import hashlib
import requests
import json

from .models import VehicleInfo


class Vehicle(object):
    """
    Vehicle class
    """

    def __init__(self, v_number, v_type, vin, url):
        self.v_number = v_number
        self.v_type = v_type
        self.vin = vin
        self.status = None
        self.msg = None
        self.data = None
        self.query_url = url

    # get vehicle info
    def get_vehicle_info(self):
        # get vehicle info from local database
        if self.get_vehicle_info_from_local():
            self.status = 0
            self.msg = '本地查询成功'
            return

        # get vehicle info from external api
        appid = '100370'
        secret = '254c0cc463d0474c6e35b1994aa7f1dd'
        sign = 'appid=%s&hphm=%s&hpzl=%s&secret=%s&vin=%s' % (appid, self.v_number, self.v_type, secret, self.vin)
        sign = hashlib.md5(sign.encode()).hexdigest()

        data = {
            "appid": appid,
            "hphm": self.v_number,
            "hpzl": self.v_type,
            "vin": self.vin,
            "sign": sign
        }

        response_data = requests.post(url=self.query_url, data=data)
        response_data = json.loads(response_data.content.decode())

        self.status = response_data.get('code', None)
        self.msg = response_data.get('msg', None)
        self.data = response_data.get('data', None)

        if self.status == 200:
            self.save_vehicle_info()

    # get vehicle info from local database
    def get_vehicle_info_from_local(self):
        try:
            vehicle_info = VehicleInfo.objects.get(hphm=self.v_number, hpzl=self.v_type, clsbdh__contains=self.vin)

            self.data = {
                'xh': vehicle_info.xh,
                'hpzl': vehicle_info.hpzl,
                'hphm': vehicle_info.hphm,
                'clpp1': vehicle_info.clpp1,
                'clxh': vehicle_info.clxh,
                'clpp2': vehicle_info.clpp2,
                'gcjk': vehicle_info.gcjk,
                'zzg': vehicle_info.zzg,
                'zzcmc': vehicle_info.zzcmc,
                'clsbdh': vehicle_info.clsbdh,
                'fdjh': vehicle_info.fdjh,
                'cllx': vehicle_info.cllx,
                'csys': vehicle_info.csys,
                'syxz': vehicle_info.syxz,
                'syr': vehicle_info.syr,
                'ccdjrq': vehicle_info.ccdjrq,
                'djrq': vehicle_info.djrq,
                'yxqz': vehicle_info.yxqz,
                'qzbfqz': vehicle_info.qzbfqz,
                'fzjg': vehicle_info.fzjg,
                'glbm': vehicle_info.glbm,
                'bxzzrq': vehicle_info.bxzzrq,
                'zt': vehicle_info.zt,
                'dybj': vehicle_info.dybj,
                'fdjxh': vehicle_info.fdjxh,
                'rlzl': vehicle_info.rlzl,
                'pl': vehicle_info.pl,
                'gl': vehicle_info.gl,
                'zxxs': vehicle_info.zxxs,
                'cwkc': vehicle_info.cwkc,
                'cwkk': vehicle_info.cwkk,
                'cwkg': vehicle_info.cwkg,
                'hxnbcd': vehicle_info.hxnbcd,
                'hxnbkd': vehicle_info.hxnbkd,
                'hxnbgd': vehicle_info.hxnbgd,
                'gbthps': vehicle_info.gbthps,
                'zs': vehicle_info.zs,
                'zj': vehicle_info.zj,
                'qlj': vehicle_info.qlj,
                'hlj': vehicle_info.hlj,
                'ltgg': vehicle_info.ltgg,
                'lts': vehicle_info.lts,
                'zzl': vehicle_info.zzl,
                'zbzl': vehicle_info.zbzl,
                'hdzzl': vehicle_info.hdzzl,
                'hdzk': vehicle_info.hdzk,
                'zqyzl': vehicle_info.zqyzl,
                'qpzk': vehicle_info.qpzk,
                'hpzk': vehicle_info.hpzk,
                'hbdbqk': vehicle_info.hbdbqk,
                'ccrq': vehicle_info.ccrq,
                'clyt': vehicle_info.clyt,
                'ytsx': vehicle_info.ytsx,
                'xszbh': vehicle_info.xszbh,
                'jyhgbzbh': vehicle_info.jyhgbzbh,
                'xzqh': vehicle_info.xzqh,
                'zsxzqh': vehicle_info.zsxzqh,
                'zzxzqh': vehicle_info.zzxzqh,
                'sgcssbwqk': vehicle_info.sgcssbwqk,
                'sfmj': vehicle_info.sfmj,
                'bmjyy': vehicle_info.bmjyy,
                'sfxny': vehicle_info.sfxny,
                'xnyzl': vehicle_info.xnyzl,
                'bz': vehicle_info.bz
            }

            return True
        except Exception as e:
            print(e)
            return False

    # save vehicle info
    def save_vehicle_info(self):
        vehicle_info = VehicleInfo()

        # vehicle_info.hphm = self.data.get('hphm', '')
        # vehicle_info.hpzl = self.data.get('hpzl', '')
        # vehicle_info.syr = self.data.get('syr', '')
        # vehicle_info.clpp1 = self.data.get('clpp1', '')
        # vehicle_info.clxh = self.data.get('clxh', '')
        # vehicle_info.clsbdh = self.data.get('clsbdh', '')
        # vehicle_info.fdjh = self.data.get('fdjh', '')
        # vehicle_info.cllx = self.data.get('cllx', '')
        # vehicle_info.csys = self.data.get('csys', '')
        # vehicle_info.syxz = self.data.get('syxz', '')
        # vehicle_info.ccdjrq = self.data.get('ccdjrq', '')
        # vehicle_info.yxqz = self.data.get('yxqz', '')
        # vehicle_info.qzbfqz = self.data.get('qzbfqz', '')
        # vehicle_info.zt = self.data.get('zt', '')
        # vehicle_info.fdjxh = self.data.get('fdjxh', '')
        # vehicle_info.rlzl = self.data.get('rlzl', '')
        # vehicle_info.pl = self.data.get('pl', '')
        # vehicle_info.gl = self.data.get('gl', '')
        # vehicle_info.zs = self.data.get('zs', '')
        # vehicle_info.zj = self.data.get('zj', '')
        # vehicle_info.qlj = self.data.get('qlj', '')
        # vehicle_info.hlj = self.data.get('hlj', '')
        # vehicle_info.zzl = self.data.get('zzl', '')
        # vehicle_info.zbzl = self.data.get('zbzl', '')
        # vehicle_info.hdzzl = self.data.get('hdzzl', '')
        # vehicle_info.hdzk = self.data.get('hdzk', '')
        # vehicle_info.ccrq = self.data.get('ccrq', '')

        vehicle_info.xh = self.data.get('xh', '')  # 机动车序号
        vehicle_info.hpzl = self.data.get('hpzl', '')  # 号牌种类
        vehicle_info.hphm = self.data.get('hphm', '')  # 号牌号码
        vehicle_info.clpp1 = self.data.get('clpp1', '')  # 中文品牌
        vehicle_info.clxh = self.data.get('clxh', '')  # 车辆型号
        vehicle_info.clpp2 = self.data.get('clpp2', '')  # 英文品牌
        vehicle_info.gcjk = self.data.get('gcjk', '')  # 国产/进口
        vehicle_info.zzg = self.data.get('zzg', '')  # 制造国
        vehicle_info.zzcmc = self.data.get('zzcmc', '')  # 制造厂名称
        vehicle_info.clsbdh = self.data.get('clsbdh', '')  # 车辆识别代号
        vehicle_info.fdjh = self.data.get('fdjh', '')  # 发动机号
        vehicle_info.cllx = self.data.get('cllx', '')  # 车辆类型
        vehicle_info.csys = self.data.get('csys', '')  # 车身颜色
        vehicle_info.syxz = self.data.get('syxz', '')  # 使用性质
        vehicle_info.syr = self.data.get('syr', '')  # 机动车所有人
        vehicle_info.ccdjrq = self.data.get('ccdjrq', '')  # 初次登记日期
        vehicle_info.djrq = self.data.get('djrq', '')  # 最近定检日期
        vehicle_info.yxqz = self.data.get('yxqz', '')  # 检验有效期止
        vehicle_info.qzbfqz = self.data.get('qzbfqz', '')  # 强制报废期止
        vehicle_info.fzjg = self.data.get('fzjg', '')  # 发证机关
        vehicle_info.glbm = self.data.get('glbm', '')  # 管理部门
        vehicle_info.bxzzrq = self.data.get('bxzzrq', '')  # 保险终止日期
        vehicle_info.zt = self.data.get('zt', '')  # 机动车状态
        vehicle_info.dybj = self.data.get('dybj', '')  # 抵押标记
        vehicle_info.fdjxh = self.data.get('fdjxh', '')  # 发动机型号
        vehicle_info.rlzl = self.data.get('rlzl', '')  # 燃料种类
        vehicle_info.pl = self.data.get('pl', '')  # 排量
        vehicle_info.gl = self.data.get('gl', '')  # 功率
        vehicle_info.zxxs = self.data.get('zxxs', '')  # 转向形式
        vehicle_info.cwkc = self.data.get('cwkc', '')  # 车外廓长
        vehicle_info.cwkk = self.data.get('cwkk', '')  # 车外廓宽
        vehicle_info.cwkg = self.data.get('cwkg', '')  # 车外廓高
        vehicle_info.hxnbcd = self.data.get('hxnbcd', '')  # 货箱内部长度
        vehicle_info.hxnbkd = self.data.get('hxnbkd', '')  # 货箱内部宽度
        vehicle_info.hxnbgd = self.data.get('hxnbgd', '')  # 货箱内部高度
        vehicle_info.gbthps = self.data.get('gbthps', '')  # 钢板弹簧片数
        vehicle_info.zs = self.data.get('zs', '')  # 轴数
        vehicle_info.zj = self.data.get('zj', '')  # 轴距
        vehicle_info.qlj = self.data.get('qlj', '')  # 前轮距
        vehicle_info.hlj = self.data.get('hlj', '')  # 后轮距
        vehicle_info.ltgg = self.data.get('ltgg', '')  # 轮胎规格
        vehicle_info.lts = self.data.get('lts', '')  # 轮胎数
        vehicle_info.zzl = self.data.get('zzl', '')  # 总质量
        vehicle_info.zbzl = self.data.get('zbzl', '')  # 整备质量
        vehicle_info.hdzzl = self.data.get('hdzzl', '')  # 核定载质量
        vehicle_info.hdzk = self.data.get('hdzk', '')  # 核定载客
        vehicle_info.zqyzl = self.data.get('zqyzl', '')  # 准牵引总质量
        vehicle_info.qpzk = self.data.get('qpzk', '')  # 驾驶室前排载客人数
        vehicle_info.hpzk = self.data.get('hpzk', '')  # 驾驶室后排载客人数
        vehicle_info.hbdbqk = self.data.get('hbdbqk', '')  # 环保达标情况
        vehicle_info.ccrq = self.data.get('ccrq', '')  # 出厂日期
        vehicle_info.clyt = self.data.get('clyt', '')  # 车辆用途
        vehicle_info.ytsx = self.data.get('ytsx', '')  # 用途属性
        vehicle_info.xszbh = self.data.get('xszbh', '')  # 行驶证证芯编号
        vehicle_info.jyhgbzbh = self.data.get('jyhgbzbh', '')  # 检验合格标志
        vehicle_info.xzqh = self.data.get('xzqh', '')  # 管理辖区
        vehicle_info.zsxzqh = self.data.get('zsxzqh', '')  # 住所地址行政区划
        vehicle_info.zzxzqh = self.data.get('zzxzqh', '')  # 联系地址行政区划
        vehicle_info.sgcssbwqk = self.data.get('sgcssbwqk', '')  # 事故车损伤部位情况
        vehicle_info.sfmj = self.data.get('sfmj', '')  # 是否免检
        vehicle_info.bmjyy = self.data.get('bmjyy', '')  # 不免检原因
        vehicle_info.sfxny = self.data.get('sfxny', '')  # 是否新能源汽车
        vehicle_info.xnyzl = self.data.get('xnyzl', '')  # 新能源汽车种类
        vehicle_info.bz = self.data.get('bz', '')  # 备注

        try:
            vehicle_info.save()
        except Exception as e:
            print(e)


















