from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from PIL import Image, ImageDraw, ImageFont
import xlrd
import xlwt

import io
import hashlib
import random

from vio_query_web.utils import MyPaginator
from vio_query_web import settings
from .models import UserInfo, VehicleInfo, VioInfo
from .decorator import login_check
from .violation import Violation

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

    request.session['username'] = username
    request.session['password'] = password

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
def vehicle_management(request):
    # 获取session中的user_id, 根据user_id查询企业
    user_id = int(request.session.get('user_id', ''))

    # 查询该企业的所有车辆数据
    if user_id != '' and user_id != 1:
        vehicle_list = VehicleInfo.objects.filter(user_id=user_id).order_by('id')
    else:
        vehicle_list = VehicleInfo.objects.all().order_by('id')

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

    context = {'mp': mp,
               'number': number,
               }

    # 保存页面状态到session
    request.session['number'] = number
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
    vehicle_type = int(request.POST.get('type', '2'))           # 车辆类型
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

    # 删除车辆
    try:
        # 根据id查询车辆
        car = VehicleInfo.objects.get(id=vehicle_id)

        # 删除与该车相关的违章信息
        vio_list = VioInfo.objects.filter(number=car.number)
        vio_list.delete()

        # 删除车辆
        car.delete()
    except Exception as e:
        print(e)

    # 构建返回url
    number = request.session.get('number', '')
    page_num = request.session.get('page_num', '')
    url = '/vehicle?number=%s&page_num=%s&' % (number, page_num)

    return HttpResponseRedirect(url)


# 是否超出查询辆限制
def is_exceed_limitation(request):
    user_id = int(request.session.get('user_id', ''))
    user_info = UserInfo.objects.get(id=user_id)

    if 0 <= user_info.limitation <= user_info.queried_number:
        result = True
    else:
        result = False

    return JsonResponse({'result': result})


# 是否可以查询全部车辆
def can_query_all(request):
    user_id = int(request.session.get('user_id', ''))
    user_info = UserInfo.objects.get(id=user_id)

    vehicle_list = VehicleInfo.objects.filter(user_id=user_id, status__in=[-1, -3])
    # print(len(vehicle_list))
    if user_info.queried_number + len(vehicle_list) > user_info.limitation:
        result = False
    else:
        result = True

    return JsonResponse({'result': result})


# 查询违章
def query_vio(request):
    vehicle_id = request.GET.get('vehicle_id', '')

    username = request.session.get('username', 'test')
    password = request.session.get('password', 'test')

    vehicle = VehicleInfo.objects.get(id=vehicle_id)

    if vehicle.status < 0:
        violation = Violation(vehicle, username, password)
        violation.get_violations_from_api()
        violation.save_violations()

        # 记录查询次数
        user_id = int(request.session.get('user_id', ''))

        try:
            user_info = UserInfo.objects.get(id=user_id)

            if vehicle.status >= 0 or vehicle.status == -2:
                user_info.queried_number += 1

            user_info.save()
        except Exception as e:
            print(e)

        number = request.session.get('number', '')
        page_num = request.session.get('page_num', '')
        url = '/vehicle?number=%s&page_num=%s&' % (number, page_num)
    else:
        url = '/vio_display?vehicle_id=' + vehicle_id

    return HttpResponseRedirect(url)


# 查询全部违章
def query_all(request):
    user_id = int(request.session.get('user_id', ''))
    username = request.session.get('username', 'test')
    password = request.session.get('password', 'test')

    vehicle_list = VehicleInfo.objects.filter(user_id=user_id).filter(status__in=[-1, -3])
    user_info = UserInfo.objects.get(id=user_id)

    for vehicle in vehicle_list:

        violation = Violation(vehicle, username, password)
        violation.get_violations_from_api()
        violation.save_violations()

        if vehicle.status >= 0 or vehicle.status == -2:
            user_info.queried_number += 1

        if user_info.queried_number >= user_info.limitation:
            break

    try:
        user_info.save()
    except Exception as e:
        print(e)

    number = request.session.get('number', '')
    page_num = request.session.get('page_num', '')
    url = '/vehicle?number=%s&page_num=%s&' % (number, page_num)

    return HttpResponseRedirect(url)


# 显示违章
def vio_display(request):
    vehicle_id = request.GET.get('vehicle_id', '')

    # 获取车辆搜索信息
    number = request.GET.get('number', '')

    # 获取用户id
    user_id = int(request.session.get('user_id', ''))

    if vehicle_id:
        vehicle = VehicleInfo.objects.get(id=vehicle_id, user_id=user_id)
        vio_list = VioInfo.objects.filter(number=vehicle.number, type=vehicle.type, user_id=user_id)
        number = vehicle.number
    elif number:
        vio_list = VioInfo.objects.filter(number=number, type=2, user_id=user_id)
    else:
        vio_list = VioInfo.objects.filter(user_id=user_id)

    # 获得用户指定的页面
    page_num = int(request.GET.get('page_num', 1))

    # 创建分页
    mp = MyPaginator()
    mp.paginate(vio_list, 10, page_num)

    # 查询是否允许提交
    context = {'mp': mp,
               'number': number,
               }

    return render(request, 'violation.html', context)


# 退出登录
def logout(request):
    request.session.clear()
    request.session.flush()

    return HttpResponseRedirect('/')


# 批量导入车辆信息
def vehicle_import(request):
    # 获取用户上传的excel文件, 文件不存储, 在内存中对文件进行操作
    excel_file = request.FILES.get('excel_file')

    # 打开excel文件, 直接从内存读取文件内容
    workbook = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
    # 获得sheets列表
    sheets = workbook.sheet_names()
    # 获得第一个sheet对象
    worksheet = workbook.sheet_by_name(sheets[0])
    # 遍历
    for i in range(1, worksheet.nrows):
        # row = worksheet.row(i)
        # 读取一条车辆信息
        # ctype： 0-empty, 1-string, 2-number, 3-date, 4-boolean, 5-error
        if worksheet.cell(i, 0).ctype == 2:
            number = str(int(worksheet.cell_value(i, 0))).replace(' ', '')     # 车牌号
        else:
            number = str(worksheet.cell_value(i, 0)).replace(' ', '')

        if worksheet.cell(i, 1).ctype == 2:
            engine = str(int(worksheet.cell_value(i, 1))).replace(' ', '')     # 发动机型号
        else:
            engine = str(worksheet.cell_value(i, 1)).replace(' ', '')

        if worksheet.cell(i, 2).ctype == 2:
            vin = str(int(worksheet.cell_value(i, 2))).replace(' ', '')     # 车架号
        else:
            vin = str(worksheet.cell_value(i, 2)).replace(' ', '')

        # 如果车牌不为空, 创建车辆对象, 否则略过该条数据
        if number == '' or number is None:
            continue
        else:
            # 如果库中该企业已经存在该车牌, 则忽略该车辆, 否者创建新的车辆对象
            # 获取session中的user_id, 根据user_id查询企业
            user_id = int(request.session.get('user_id', ''))

        # 查询该企业的所有车辆数据
        if user_id == '':
            continue
        else:
            exist_truck_list = VehicleInfo.objects.filter(user_id=user_id).filter(number=number)

        if exist_truck_list:
            vehicle = exist_truck_list[0]
            if vehicle.status == -2:
                vehicle.status = -1
        else:
            vehicle = VehicleInfo()
            vehicle.number = number

        # 添加车辆属性
        vehicle.type = 2
        vehicle.engine = engine if engine else None
        vehicle.vin = vin if vin else None
        vehicle.user_id = user_id

        vehicle.save()

    # 构建返回url
    number = request.session.get('number', '')
    page_num = request.session.get('page_num', '')
    url = '/vehicle?number=%s&page_num=%s' % (number, page_num)

    return HttpResponseRedirect(url)


# 导出违章数据
def vio_export(request):

    user_id = request.session.get('user_id', None)

    if user_id:
        vio_list = VioInfo.objects.filter(user_id=user_id)
    else:
        vio_list = VioInfo.objects.all()

    if vio_list:

        # 创建工作簿
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('sheet1', cell_overwrite_ok=True)

        # 设置表头
        title = ['车牌号码', '车辆类型', '违法时间', '违法地点', '违法行为', '扣分', '罚款', '处理状态', '缴费状态']

        # 生成表头
        len_col = len(title)
        for i in range(0, len_col):
            ws.write(0, i, title[i])

        # 写入车辆数据
        i = 1
        for vio in vio_list:
            # 读取违章数据
            vehicle_number = vio.number
            vehicle_type = vio.type
            vehicle_time = vio.time
            vehicle_position = vio.position
            vehicle_activity = vio.activity
            vehicle_point = vio.point
            vehicle_money = vio.money

            if vio.deal_status == 1:
                vehicle_deal = '已处理'
            elif vio.deal_status == 0:
                vehicle_deal = '未处理'
            else:
                vehicle_deal = '未知'

            if vio.pay_status == 1:
                vehicle_pay = '已缴费'
            elif vio.pay_status == 0:
                vehicle_pay = '未缴费'
            else:
                vehicle_pay = '未知'

            content = [vehicle_number,
                       vehicle_type,
                       vehicle_time,
                       vehicle_position,
                       vehicle_activity,
                       vehicle_point,
                       vehicle_money,
                       vehicle_deal,
                       vehicle_pay
                       ]

            for j in range(0, len_col):
                ws.write(i, j, content[j])
            i += 1

        # 内存文件操作
        buf = io.BytesIO()

        # 将文件保存在内存中
        wb.save(buf)
        response = HttpResponse(buf.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=violations.xls'
        response.write(buf.getvalue())
        return response
    else:
        # 构建返回url
        number = request.session.get('number', '')
        page_num = request.session.get('page_num', '')
        url = '/vehicle?number=%s&page_num=%s' % (number, page_num)

        return HttpResponseRedirect(url)


# 删除全部车辆
def delete_all_vehicle(request):
    user_id = int(request.session.get('user_id', ''))

    try:
        vehicle_list = VehicleInfo.objects.filter(user_id=user_id)
        vehicle_list.delete()
    except Exception as e:
        print(e)

    return render(request, 'vehicle.html')


# 删除全部违章
def delete_all_violation(request):
    user_id = int(request.session.get('user_id', ''))

    try:
        vio_list = VioInfo.objects.filter(user_id=user_id)
        vio_list.delete()

        VehicleInfo.objects.exclude(status__in=[-2, -4]).update(status=-1)
    except Exception as e:
        print(e)

    return render(request, 'violation.html')


# 删除全部车辆和违章
def delete_all(request):
    user_id = int(request.session.get('user_id', ''))

    try:
        vio_list = VioInfo.objects.filter(user_id=user_id)
        vio_list.delete()

        vehicle_list = VehicleInfo.objects.filter(user_id=user_id)
        vehicle_list.delete()
    except Exception as e:
        print(e)

    return render(request, 'vehicle.html')


# 显示用户管理页面
def user_show(request):
    username = request.GET.get('username', '')

    if username:
        user_list = UserInfo.objects.filter(username=username)
    else:
        user_list = UserInfo.objects.all()

    # 获得用户指定的页面
    page_num = int(request.GET.get('page_num', 1))

    # 创建分页
    mp = MyPaginator()
    mp.paginate(user_list, 10, page_num)

    # 查询是否允许提交
    context = {'mp': mp,
               'username': username,
               }

    # 保存页面状态到session
    request.session['username'] = username
    request.session['page_num'] = page_num

    return render(request, 'user.html', context)


# 判断用户是否存在
def is_user_exist(request):
    username = request.GET.get('username', '')

    result = UserInfo.objects.filter(username=username).exists()

    return JsonResponse({'result': result})


# 新增用户
def user_add(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    authority = request.POST.get('authority', 1)

    user = UserInfo()
    user.username = username
    user.password = hashlib.sha1(password.encode('utf8')).hexdigest()
    user.authority = int(authority)

    try:
        user.save()
    except Exception as e:
        print(e)

    # 构建返回url
    username = request.session.get('username', '')
    page_num = request.session.get('page_num', '')
    url = '/user_show?username=%s&page_num=%s&' % (username, page_num)

    return HttpResponseRedirect(url)





