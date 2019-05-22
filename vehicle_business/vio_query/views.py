from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from PIL import Image, ImageDraw, ImageFont

import io
import hashlib
import random

from vehicle_business.utils import MyPaginator
from vehicle_business import settings
from .models import UserInfo, VehicleInfo
from .decorator import login_check

# Create your views here.


def login(request):
    # session中的user_id不等于空直接跳转到主页
    user_id = request.session.get('user_id', '')
    if user_id != '':
        return HttpResponseRedirect('/main')

    msg = request.GET.get('msg', '')

    context = {'msg': msg}

    return render(request, 'login.html', context)


# 登陆服务
def login_handle(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    code = request.POST.get('check_code').upper()

    session_code = request.session.get('check_code')

    if code != session_code:
        msg = '验证码错误'
        return HttpResponseRedirect('/?msg=%s' % msg)

    user_list = UserInfo.objects.filter(username=username)
    if len(user_list) == 0:
        msg = '用户不存在'
        return HttpResponseRedirect('/?msg=%s' % msg)

    user = user_list[0]
    if hashlib.sha1(password.encode('utf8')).hexdigest() != user.password:
        msg = '用户名或密码错误'
        return HttpResponseRedirect('/?msg=%s' % msg)

    # 把user.id保存到session中
    request.session.set_expiry(0)  # 浏览器关闭后清除session
    request.session['user_id'] = user.id
    request.session['authority'] = user.authority

    return HttpResponseRedirect('/main')


# 退出登录
def logout(request):
    request.session.clear()
    request.session.flush()

    return HttpResponseRedirect('/')


# 验证码
def check_code(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (255, 255, 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (0, 0, 0)
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD23EFGHJK456LMNPQRS789TUVWXYZ'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 设置字体
    font = ImageFont.truetype(r"%s/simsun.ttf" % settings.FONTS_DIR, 23)
    # 字体颜色
    fontcolor = (0, 0, 0)
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    # 存入session，用于做进一步验证
    request.session['check_code'] = rand_str
    request.session.set_expiry(0)  # 浏览器关闭后清除session
    # 内存文件操作
    buf = io.BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


# 显示主页面
@login_check
def main(request):
    user_id = request.session.get('user_id', '')

    if user_id != '':
        user = UserInfo.objects.filter(id=user_id)[0]
    # 这里有点问题, user不一定有值, 后面得修改
    context = {'user': user}

    return render(request, 'main.html', context)


# 显示车辆管理页面
@login_check
def vehicle(request):
    # 获取session中的user_id, 根据user_id查询企业
    user_id = int(request.session.get('user_id', ''))

    # 查询该企业的所有车辆数据
    if user_id != '' and user_id != 1:
        vehicle_list = VehicleInfo.objects.filter(enterprise_id=user_id).order_by('id')
    else:
        vehicle_list = VehicleInfo.objects.all().order_by('id')

    # 获取用户选择的车辆查询状态
    status = int(request.GET.get('status', 0))

    # 获取车辆搜索信息
    number = request.GET.get('number', '')

    # 在结果集中搜索包含搜索信息的车辆, 车辆搜索功能不完善, 指数如车牌号,不要输入号牌所在地
    if number != '':
        vehicle_list = vehicle_list.filter(number__contains=number)

    # 获得用户指定的页面
    page_num = int(request.GET.get('page_num', 1))

    # 创建分页
    mp = MyPaginator()
    mp.paginate(vehicle_list, 10, page_num)

    # 查询是否允许提交

    context = {'mp': mp,
               'number': number,
               'user_id': user_id,
               'status': status,
               }

    # 保存页面状态到session
    request.session['number'] = number
    request.session['status'] = status
    request.session['page_num'] = page_num

    return render(request, 'vehicle.html', context)


# 判断该号牌车辆是否已经存在
def is_vehicle_exist(request):
    user_id = int(request.session.get('user_id', ''))
    number = request.GET.get('number', '')
    origin_number = request.GET.get('origin_number', '')

    result = False

    if number != origin_number:
        result = VehicleInfo.objects.filter(number=number).filter(user_id=user_id).exists()

    return JsonResponse({'result': result})


# 添加车辆
def vehicle_add(request):
    # 获取用户提交的车辆信息

    number = request.POST.get('number', '')                     # 号牌号码
    engine = request.POST.get('engine', '')                     # 发动机号
    vehicle_type = int(request.POST.get('type', '2'))            # 车辆类型
    vin = request.POST.get('vin', '')                           # 车架号

    # 创建车辆数据对象
    car = VehicleInfo()
    car.type = vehicle_type
    car.number = number
    car.engine = engine
    car.vin = vin

    # 获取session中的user_id, 根据user_id查询企业
    user_id = int(request.session.get('user_id', ''))

    # 车辆属于哪个用户
    if user_id != '' and user_id != 1:
        car.user_id = user_id
    else:
        car.user_id = 1

    # 存入数据库
    try:
        car.save()
    except Exception as e:
        print(e)

    # 构建返回url
    number = request.session.get('number', '')
    page_num = request.session.get('page_num', '')
    url = '/vehicle?number=%s&page_num=%s' % (number, page_num)

    return HttpResponseRedirect(url)


# 编辑车辆
def vehicle_modify(request):

    # 获取用户提交的车辆信息
    number = request.POST.get('number', '')                     # 号牌号码
    engine = request.POST.get('engine', '')                     # 发动机号
    vehicle_type = int(request.POST.get('type', '2'))           # 车辆类型
    vin = request.POST.get('vin', '')                           # 车架号
    vehicle_id = request.POST.get('vehicle_id')

    # 创建车辆数据对象
    car = VehicleInfo.objects.get(id=vehicle_id)
    car.type = vehicle_type
    car.number = number
    car.engine = engine
    car.vin = vin

    # 存入数据库
    try:
        car.save()
    except Exception as e:
        print(e)

    # 构建返回url
    number = request.session.get('number', '')
    page_num = request.session.get('page_num', '')
    url = '/vehicle?number=%s&page_num=%s' % (number, page_num)

    return HttpResponseRedirect(url)


# 删除车辆
def vehicle_delete(request):
    # 获取车辆id
    vehicle_id = request.POST.get('vehicle_id')  # 车辆id

    # 根据id查询车辆
    car = VehicleInfo.objects.get(id=vehicle_id)

    # 删除车辆
    try:
        car.delete()
    except Exception as e:
        print(e)

    # 构建返回url
    number = request.session.get('number', '')
    page_num = request.session.get('page_num', '')
    url = '/vehicle?number=%s&page_num=%s&' % (number, page_num)

    return HttpResponseRedirect(url)


# 查询违章
def query_vio(request):
    vehicle_id = request.GET.get('vehicle_id', '')

    if vehicle_id:
        car = car = VehicleInfo.objects.get(id=vehicle_id)



