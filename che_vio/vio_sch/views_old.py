"""
老接口应用
"""
from django.http import JsonResponse, HttpResponse
from .models import UserInfo
import base64
import json
import time
import hashlib


# 用户登录
def login_service(request):
    # 不接收get方式请求
    if request.method == 'GET':
        response_data = {'status': 31, 'message': 'request method error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断请求ip是否在白名单中
    # if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
    #     user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    # else:
    #     user_ip = request.META['REMOTE_ADDR']

    # 如果ip不在白名单返回状态码14, 暂不验证ip
    # if not IpInfo.objects.filter(ip_addr=user_ip).exists():
    #     result = {'status': 14}
    #     return JsonResponse(result)

    # 获取用户传递的参数
    param = request.POST.get('param', '')
    print(param)
    if param == '':
        response_data = {'status': 99, 'message': 'request invalid'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    param = json.loads(base64.b64decode(param).decode('utf-8').replace('\'', '\"'))

    try:
        # 获取用户名和密码
        username = param['username']
        password = param['password']
        print('%s : %s' % (username, password))

        # 对比用户和密码
        user = UserInfo.objects.filter(username=username).get(password=password)

        # 如果用户信息正确, 记录当前时间戳
        user.timestamp = int(time.time())
        user.save()
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'username or password error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 根据用户名密码和时间戳计算token
    token = '%s%d%s' % (username, user.timestamp, password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()

    # 构造返回数据
    response_data = base64.b64encode(json.dumps({'status': 0, 'token': token}).encode('utf-8'))

    return HttpResponse(response_data)


# 查询违章
def violation_service(request):
    # 获取用户传递的参数
    param = request.POST.get('param', '')

    if param == '':
        response_data = {'status': 99, 'message': 'request invalid'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    param = json.loads(base64.b64decode(param).decode('utf-8').replace('\'', '\"'))

    try:
        # 获取用户名和密码
        username = param['userId']
        user_token = param['token']

        # 对比用户和密码
        user = UserInfo.objects.get(username=username)
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'user info error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 计算token
    token = '%s%d%s' % (username, user.timestamp, user.password)
    token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()

    # 对比token
    if token != user_token:
        response_data = {'status': 5, 'message': 'user is not login'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断车辆类型
    try:
        v_type = int(param['vehicleType'])
        if v_type < 10:
            v_type = '0%d' % v_type
        else:
            v_type = str(v_type)
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'vehicle type error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断车牌号
    try:
        v_number = param['vehicleNumber']
        if v_type == '02' and len(v_number) < 7:
            raise Exception
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'vehicle parameters error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    # 判断车辆识别代号, 发动机号
    try:
        vin = param['vin']
        e_code = param['e_code']
    except Exception as e:
        print(e)
        response_data = {'status': 5, 'message': 'vin or engine code error'}
        response_data = base64.b64encode(json.dumps(response_data).encode('utf-8'))
        return HttpResponse(response_data)

    if 'city' in param:
        city = param['city']
    else:
        city = ''
