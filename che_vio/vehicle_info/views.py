from django.http import JsonResponse
from.forms import SearchForm
from .user import User


# Create your views here.


#  查询车辆信息
def vehicle_info(request):
    # 获取请求ip
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    # 获取请求表单对象
    if request.method == 'GET':
        form_obj = SearchForm(request.GET)
    else:
        form_obj = SearchForm(request.POST)

    # 表单数据无效
    if not form_obj.is_valid():
        result = {'status': 99, 'msg': '请求数据无效'}
        return JsonResponse(result)

    # 获取请求表单对象
    if request.method == 'GET':
        form_obj = SearchForm(request.GET)
    else:
        form_obj = SearchForm(request.POST)

    user = User(form_obj.username, form_obj.timestamp, form_obj.sign, user_ip)

    if not user.check_user():
        user.create_result()
        return JsonResponse(user.query_result)

    if not user.get_url():
        user.create_result()
        return JsonResponse(user.query_result)





















