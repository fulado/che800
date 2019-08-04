"""
forms.py
用户请求表单
"""

from django import forms


class SearchForm(forms.Form):
    username = forms.CharField()            # 用户名
    timestamp = forms.CharField()        # 时间戳
    sign = forms.CharField()                # 校验信息
    vehicleType = forms.CharField()         # 号牌类型
    vehicleNumber = forms.CharField()       # 号牌号码
    vin = forms.CharField()                 # 车架号

