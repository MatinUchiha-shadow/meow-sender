#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ارسال خودکار «میو» روی GitHub Actions — ۲۴ ساعته و رایگان، حتی با لپ‌تاپ خاموش
==============================================================================
نحوه کار:
  - متن پیام از schedule.json خونده می‌شه
  - آیدی گروه از Secret به نام TELEGRAM_CHAT_ID خونده می‌شه
  - سشن اکانتت (که با دکمه «آماده‌سازی برای گیت‌هاب» داخل میو‌سندر کپی شد)
    از Secret به نام TELEGRAM_SESSION خونده و رمزگشایی می‌شه

اجرای تست لوکال:
    TELEGRAM_SESSION=<base64> TELEGRAM_CHAT_ID=-1001234567890 python send.py
"""
import asyncio
import base64
import gzip
import json
import os
import sys
import tempfile

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"


async def main():
    from telethon import TelegramClient

    b64 = os.environ.get("TELEGRAM_SESSION", "").strip()
    chat_id_raw = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not b64:
        print("خطا: Secret به نام TELEGRAM_SESSION تنظیم نشده.")
        sys.exit(1)
    if not chat_id_raw:
        print("خطا: Secret به نام TELEGRAM_CHAT_ID تنظیم نشده.")
        sys.exit(1)
    try:
        chat_id = int(chat_id_raw)
    except ValueError:
        print(f"خطا: TELEGRAM_CHAT_ID عدد نیست: {chat_id_raw!r}")
        sys.exit(1)

    try:
        with open("schedule.json", encoding="utf-8") as f:
            sched = json.load(f)
        text = sched.get("text", "میو")
    except Exception as e:
        print(f"خطا: schedule.json خونده نشد — {e}")
        sys.exit(1)

    # سشن (فایل SQLite) از base64 بازسازی می‌شه.
    # نکته مهم: اسم فایل باید حتماً به .session ختم بشه وگرنه Telethon
    # خودش پسوند رو اضافه می‌کنه و دنبال فایل اشتباه می‌گرده.
    tmp = tempfile.mkdtemp(prefix="meow_gh_")
    session_path = os.path.join(tmp, "meow_session.session")
    try:
        data = base64.b64decode(b64)
        # سشن میو‌سندر فشرده (gzip) کپی می‌کنه تا زیر سقف ۶۴KB سکرت گیت‌هاب بمونه
        if data[:2] == b"\x1f\x8b":
            data = gzip.decompress(data)
        with open(session_path, "wb") as f:
            f.write(data)
    except Exception as e:
        print(f"خطا: TELEGRAM_SESSION قابل رمزگشایی نیست — {e}")
        sys.exit(1)

    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("خطا: سشن معتبر نیست.")
        print("ممکنه برنامه میو‌سندر هم‌زمان باز باشه — همون سشن از دو جا نمی‌تونه استفاده بشه.")
        print("برنامه رو ببند، دوباره سشن رو کپی کن و Secret رو عوض کن.")
        sys.exit(1)

    me = await client.get_me()
    entity = await client.get_entity(chat_id)
    await client.send_message(entity, text)
    print(f"OK: «{text}» به {chat_id} فرستاده شد (اکانت: {me.first_name})")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
