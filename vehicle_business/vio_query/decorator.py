from django.shortcuts import redirect


# 判断用户是否登录，如果没有登录这跳转到登录页
def login_check(func):
    def wrapped(request, *args, **kwargs):
        if request.session.get('user_id'):  # 如果session中没有存储用户的登录信息
            return func(request, *args, **kwargs)
        else:
            return redirect('/')

    return wrapped

