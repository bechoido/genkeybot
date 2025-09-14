import os
import json
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# === Crypto key (phải giống với license_manager.py) ===
AES_KEY = b'IPvFoQKYZS7yTERTArJSI4U3qbb5TQgGqqmGKbzR-yg='
FERNET = Fernet(AES_KEY)

LICENSE_SCHEMA_V3 = 3
LICENSE_DAYS_DEFAULT = 30

# =============================================================
# Utils
# =============================================================
def pc_hash(pc_name: str) -> str:
    """Hash PC name -> PC Hash (12 ký tự)"""
    h = hashlib.sha256(pc_name.upper().encode()).hexdigest()
    return h[:12].upper()

# =============================================================
# V3 license logic
# =============================================================
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

def admin_make_v3_key(pc_name: str, days: int, app_version: str) -> str:
    payload = make_v3_payload(pc_name=pc_name, days=days, app_version=app_version)
    return encode_v3_key(payload)

# =============================================================
# Telegram Bot handlers
# =============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = text.split()

    if len(parts) < 3:
        await update.message.reply_text("❌ Vui lòng nhập: PCNAME DAYS APP_VERSION\nVí dụ: LAPTOP123 5 1.6.0")
        return

    pc_name = parts[0]

    # Parse days
    try:
        days = int(parts[1])
    except ValueError:
        await update.message.reply_text("❌ Số ngày không hợp lệ, dùng mặc định 30 ngày.")
        days = LICENSE_DAYS_DEFAULT

    # App version (admin nhập vào)
    app_version = parts[2]

    try:
        key = admin_make_v3_key(pc_name, days=days, app_version=app_version)
        msg = f"{key}"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi tạo key: {e}")

# =============================================================
# Main
# =============================================================
if __name__ == "__main__":
    TOKEN = "8233111404:AAGd_lU0dsKIIi_5w8BDSjj5_jy89fVwqEw"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
