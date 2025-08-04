import hashlib
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Giả định phiên bản app, thay bằng import nếu bạn có module riêng
APP_VERSION = "1.0.3"

# Hàm sinh key từ seed
def generate_key(seed: str) -> str:
    hashed = hashlib.sha256(seed.encode()).digest()
    return hashed[:8].hex().upper()

# Xử lý lệnh /genkey
async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ Vui lòng nhập đúng định dạng:\n/genkey <pc_name> <seed>")
        return

    pc_name = context.args[0].strip()
    seed = context.args[1].strip()

    try:
        key = generate_key(seed)
        license_entry = {
            "pc_name": pc_name,
            "seed": seed,
            "key": key,
            "app_version": APP_VERSION,
            "note": "App của bạn đã hết hạn, liên hệ Admin"
        }

        json_text = json.dumps(license_entry, indent=2, ensure_ascii=False)
        await update.message.reply_text(f"```json\n{json_text}\n```", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi tạo key: {e}")

# Main
if __name__ == "__main__":
    # Thay bằng token bạn nhận từ BotFather
    TOKEN = "8233111404:AAGd_lU0dsKIIi_5w8BDSjj5_jy89fVwqEw"

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("genkey", genkey_command))
    app.run_polling()
