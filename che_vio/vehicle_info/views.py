from django.http import JsonResponse
from .forms import SearchForm
from .user import User
from .vehicle import Vehicle


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

    # get request data
    request_data = form_obj.clean()

    # create user object
    user = User(request_data['username'], request_data['timestamp'], request_data['sign'], user_ip,
                request_data['vehicleNumber'], request_data['vehicleType'], request_data['vin'])

    # check user info
    if not user.check_user():
        user.create_result()
        return JsonResponse(user.query_result)

    # get query url
    if not user.get_url():
        user.create_result()
        return JsonResponse(user.query_result)

    # create vehicle object
    vehicle = Vehicle(user.v_number, user.v_type, user.vin, user.query_url)

    # get vehicle info
    if vehicle.get_vehicle_info():
        vehicle.save_vehicle_info()

    # return query result
    user.vehicle = vehicle
    user.create_result()
    return JsonResponse(user.query_result)





















