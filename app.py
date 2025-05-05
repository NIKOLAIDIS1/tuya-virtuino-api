from flask import Flask, jsonify
import requests, time, hmac, hashlib

app = Flask(__name__)

@app.route('/')
def home():
    return "Tuya Azure API ready"

@app.route('/tuya/on')
def tuya_on():
    token = get_access_token()
    device_id = "test_device_id_123456"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "commands": [{"code": "switch_1", "value": True}]
    }
    url = f"https://openapi.tuyaeu.com/v1.0/devices/{device_id}/commands"
    res = requests.post(url, headers=headers, json=data)
    return jsonify(res.json())

def get_access_token():
    client_id = "test_client_id"
    secret = "test_client_secret"
    t = str(int(time.time() * 1000))
    message = client_id + t
    sign = hmac.new(secret.encode(), msg=message.encode(), digestmod=hashlib.sha256).hexdigest().upper()

    headers = {
        "t": t,
        "client_id": client_id,
        "sign": sign,
        "sign_method": "HMAC-SHA256"
    }
    url = "https://openapi.tuyaeu.com/v1.0/token?grant_type=1"
    res = requests.get(url, headers=headers)
    return res.json().get("result", {}).get("access_token", "no_token_returned")
