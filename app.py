from flask import Flask, jsonify
import requests, time, hmac, hashlib

app = Flask(__name__)

CLIENT_ID = "8nggyqkwcq3jmqqfgkcu"
CLIENT_SECRET = "caf10f42521e49bcac64f9ab2a15fa5c"
DEVICE_ID = "bfaa2a97bacdd69156wyj9"

@app.route('/')
def home():
    return "Tuya Azure API ready"

@app.route('/tuya/on')
def tuya_on():
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "commands": [{"code": "switch_1", "value": True}]
    }
    url = f"https://openapi.tuyaeu.com/v1.0/devices/{DEVICE_ID}/commands"
    res = requests.post(url, headers=headers, json=data)
    return jsonify(res.json())

def get_access_token():
    t = str(int(time.time() * 1000))
    message = CLIENT_ID + t
    sign = hmac.new(CLIENT_SECRET.encode(), msg=message.encode(), digestmod=hashlib.sha256).hexdigest().upper()

    headers = {
        "t": t,
        "client_id": CLIENT_ID,
        "sign": sign,
        "sign_method": "HMAC-SHA256"
    }
    url = "https://openapi.tuyaeu.com/v1.0/token?grant_type=1"
    res = requests.get(url, headers=headers)
    return res.json().get("result", {}).get("access_token", "no_token")
