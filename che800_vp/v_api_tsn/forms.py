"""
forms.py
用户请求表单
"""

from django import forms


class SearchForm(forms.Form):
    username = forms.CharField()            # 用户名
    timestamp = forms.IntegerField()        # 时间戳
    sign = forms.CharField()                # 校验信息
    vehicleType = forms.CharField()         # 号牌类型
    vehicleNumber = forms.CharField()       # 号牌号码
    # vehicleCode = forms.CharField(required=False)         # 车架号
    engineerCode = forms.CharField(required=False)        # 发动机号
