import requests
import json

url = "http://m1.tme-crypto.fr:8888/"
headers = {
    'Content-Type': 'application/json',
}

# data = {
#     "jsonrpc": "2.0",
#     "method": "kerberos.authentication-service",
#     "params": {"username": "niccolo"},
#     "id": 737
# }

data = {
    "jsonrpc": "2.0",
    "method": "room.items",
        "params": {"world_id":"807b4a5d685915218c7987708c110cbe", "room":"488aee50c397570f8d460223833eba7f"},
    "id": 737
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.text)

#
# import time
# import openssl
#
# d = {'username': 'toto', 'timestamp': time.time()}
# e = json.dumps(d)
# f = openssl.encrypt(e, 'foobar')
# print(f)
