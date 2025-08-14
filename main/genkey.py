import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# AES secret key
SECRET = b"111222333444555X"  # 16 bytes

# Padding cho AES
def pad(data: bytes) -> bytes:
    padder = padding.PKCS7(128).padder()
    return padder.update(data) + padder.finalize()

# Hàm sinh key từ seed bằng AES-ECB
def generate_key(seed: str) -> str:
    cipher = Cipher(algorithms.AES(SECRET), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_data = pad(seed.encode())
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted).decode()

# Xử lý lệnh /genkey
async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Vui lòng nhập seed:\n/genkey <seed>")
        return

    seed = context.args[0].strip().upper()
    try:
        key = generate_key(seed)
        await update.message.reply_text(f"🔑 Key: {key}")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi tạo key: {e}")

# Main
if __name__ == "__main__":
    TOKEN = "8233111404:AAGd_lU0dsKIIi_5w8BDSjj5_jy89fVwqEw"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("genkey", genkey_command))
    app.run_polling()
