"""
Violation query request class
"""
import time
import json
import base64
import hashlib


from .models import UserInfo


class VioRequest(object):
    """
    Violation request class
    """

    def __init__(self, request):
        """Initialize a request instance"""
        self.request = request
        self.status = 0
        self.request_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
            self.request_ip = request.META['HTTP e_code=ecode_X_FORWARDED_FOR']
        else:
            self.request_ip = request.META['REMOTE_ADDR']

        self.response_content = ''

    def login(self):
        """Login"""
        # 获取用户传递的参数
        param = self.request.POST.get('param', '')

        if param == '':
            self.status = 99
            return

        param = json.loads(base64.b64decode(param).decode('utf-8').replace('\'', '\"'))

        try:
            # 获取用户名和密码
            username = param['username']
            password = param['password']

            # 对比用户和密码
            user = UserInfo.objects.filter(username=username).get(password=password)

            # 如果用户信息正确, 记录当前时间戳
            user.timestamp = int(time.time())

            user.save()
        except Exception as e:
            print(e)
            self.status = 1
            return

        # 根据用户名密码和时间戳计算token
        token = '%s%d%s' % (username, user.timestamp, password)
        token = hashlib.sha1(token.encode('utf-8')).hexdigest().upper()
