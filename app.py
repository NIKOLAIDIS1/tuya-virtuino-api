from flask import Flask, jsonify
from datetime import datetime
import os
import hmac, hashlib, requests

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)

# -------------------------------------------------
#  Περιβάλλον &  μυστικά
# -------------------------------------------------
TUYA_CLIENT_ID = os.getenv("TUYA_CLIENT_ID")          # π.χ. ay1534…
VAULT_NAME     = os.getenv("VAULT_NAME")              # π.χ. my‑kv‑prod

# Τραβάμε το Tuya CLIENT_SECRET από το Key Vault
credential     = DefaultAzureCredential()
kv             = SecretClient(
    vault_url=f"https://{VAULT_NAME}.vault.azure.net",
    credential=credential
)
CLIENT_SECRET  = kv.get_secret("TuyaClientSecret").value


# -------------------------------------------------
#  Helper – υπογραφή HMAC‑SHA256 για Tuya API
# -------------------------------------------------
def tuya_sign(client_id: str, secret: str, t: str, s2s: str) -> str:
    msg = client_id + t + s2s
    return hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest().upper()


# -------------------------------------------------
#  /token endpoint
# -------------------------------------------------
@app.route("/token", methods=["GET"])
def token():
    """
    Επιστρέφει νέο Tuya cloud token.
    - grant_type 1 = client credentials
    """
    s2s = "GET\nSHA256\n\n/v1.0/token?grant_type=1"
    t   = str(int(datetime.utcnow().timestamp() * 1000))   # ms UTC
    sign = tuya_sign(TUYA_CLIENT_ID, CLIENT_SECRET, t, s2s)

    resp = requests.get(
        "https://openapi.tuyaeu.com/v1.0/token",
        params={"grant_type": 1},
        headers={
            "client_id":   TUYA_CLIENT_ID,
            "t":           t,
            "sign":        sign,
            "sign_method": "HMAC-SHA256",
            "lang":        "en"
        },
        timeout=10
    )

    # Επιστρέφουμε ό,τι μας δίνει η Tuya σε JSON
    return jsonify(resp.json()), resp.status_code


# -------------------------------------------------
#  Local run
# -------------------------------------------------
if __name__ == "__main__":
    # Για τοπικό dev:  flask run ή python app.py
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
    
