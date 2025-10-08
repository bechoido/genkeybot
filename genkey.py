import os
import json
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify

# =============================================================
# Config
# =============================================================
AES_KEY = b'IPvFoQKYZS7yTERTArJSI4U3qbb5TQgGqqmGKbzR-yg='
FERNET = Fernet(AES_KEY)

LICENSE_SCHEMA_V3 = 3
LICENSE_DAYS_DEFAULT = 10  # mặc định 10 ngày
APP_VERSION = "1.6.0"      # version cố định do admin quy định

# =============================================================
# Utils
# =============================================================
def pc_hash(pc_name: str) -> str:
    """Hash PC name -> PC Hash (12 ký tự)"""
    h = hashlib.sha256(pc_name.upper().encode()).hexdigest()
    return h[:12].upper()

def make_v3_payload(pc_name: str, days: int = LICENSE_DAYS_DEFAULT,
                    issued: str = None, app_version: str = None) -> dict:
    if issued is None:
        issued = datetime.now().strftime("%Y-%m-%d")
    if app_version is None:
        raise ValueError("App version must be provided")
    return {
        "schema": LICENSE_SCHEMA_V3,
        "pc": pc_hash(pc_name),
        "pc_name": pc_name,
        "issued": issued,
        "days": int(days),
        "app_version": app_version,
        "rand": os.urandom(8).hex().upper(),
    }

def encode_v3_key(payload: dict) -> str:
    blob = json.dumps(payload, separators=(",", ":")).encode()
    token = FERNET.encrypt(blob).decode()
    return f"V3.{token}"

def admin_make_v3_key(pc_name: str) -> str:
    payload = make_v3_payload(pc_name=pc_name,
                              days=LICENSE_DAYS_DEFAULT,
                              app_version=APP_VERSION)
    return encode_v3_key(payload)

# =============================================================
# Flask API
# =============================================================
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "License API is running",
        "usage": "POST /generate_key or /teams_webhook",
        "format": "/genkey <PCNAME>"
    })

@app.route("/generate_key", methods=["POST"])
def generate_key():
    """
    Endpoint chính để Power Automate gọi.
    Body JSON: {"message": "/genkey Desktop123"}
    """
    try:
        data = request.get_json(force=True)
        message = data.get("message", "").strip()

        if not message.lower().startswith("/genkey"):
            return jsonify({
                "status": "error",
                "message": "Sai cú pháp. Dùng: /genkey <PCNAME>"
            }), 400

        parts = message.split()
        if len(parts) < 2:
            return jsonify({
                "status": "error",
                "message": "Thiếu PC name. Ví dụ: /genkey LAPTOP123"
            }), 400

        pc_name = parts[1].strip()

        key = admin_make_v3_key(pc_name)
        return jsonify({
            "status": "ok",
            "pc_name": pc_name,
            "days": LICENSE_DAYS_DEFAULT,
            "app_version": APP_VERSION,
            "key": key
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =============================================================
# Main (local run)
# =============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
