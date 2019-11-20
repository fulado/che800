import hashlib
import pprint


# Create your tests here.


def get_vehicle_info(v_number, v_type, vin):

    # get vehicle info from external api
    appid = '100370'
    secret = '254c0cc463d0474c6e35b1994aa7f1dd'
    sign = 'appid=%s&hphm=%s&hpzl=%s&secret=%s&vin=%s' % (appid, v_number, v_type, secret, vin)
    sign = hashlib.md5(sign.encode()).hexdigest()

    data = {
        "appid": appid,
        "hphm": v_number,
        "hpzl": v_type,
        "vin": vin,
        "sign": sign
    }

    pprint.pprint(data)


if __name__ == '__main__':
    v_number = '川A5P27T'
    v_type = '02'
    vin = 'LH17CKBF8FH064624'
    get_vehicle_info(v_number, v_type, vin)
