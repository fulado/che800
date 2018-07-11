"""
老接口应用
"""
from django.http import JsonResponse


def register_service(request):
    # 不接收get方式请求
    if request.method == 'GET':
        return JsonResponse({'status': 31, 'message': 'request method error'})

    # 判断请求ip是否在白名单中
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        user_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
    else:
        user_ip = request.META['REMOTE_ADDR']

    # 如果ip不在白名单返回状态码14,
    # if not IpInfo.objects.filter(ip_addr=ip_addr).exists():
    #     result = {'status': 14}
    #     return JsonResponse(result)

    request_data = request.POST.get('param', '')
