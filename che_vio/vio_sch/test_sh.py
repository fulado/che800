import requests
import json


def get_vio_for_wantong(v_number, v_type, e_code):
    url = 'http://api.haoyi.link/api/Sh_yangche'

    app_key = 'mW11sLBS2DIOVdSV'
    app_secret = 'JlvNdWPQuaTm8GfKJRVCSJ0lCfxdXGuo'

    data = {'appkey': app_key,
            'appsecret': app_secret,
            'cx': v_type,
            'cp': v_number,
            'fdj': e_code
            }

    response_data = requests.get(url, data)

    print(json.loads(response_data.content.decode()))


if __name__ == '__main__':
    v_number = '沪A12345'
    v_type = '02'
    e_code = '12345'

    get_vio_for_wantong(v_number, v_type, e_code)
