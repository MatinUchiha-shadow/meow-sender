#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ارسال خودکار «میو» روی GitHub Actions — ۲۴ ساعته و رایگان، حتی با لپ‌تاپ خاموش
==============================================================================
نحوه کار:
  - متن پیام از schedule.json خونده می‌شه
  - آیدی گروه از Secret به نام TELEGRAM_CHAT_ID خونده می‌شه
  - سشن اکانتت (که با دکمه «آماده‌سازی برای گیت‌هاب» داخل میو‌سندر کپی شد)
    به صورت StringSession از Secret به نام TELEGRAM_SESSION خونده می‌شه

اجرای تست لوکال:
    TELEGRAM_SESSION=<string> TELEGRAM_CHAT_ID=-1001234567890 python send.py
"""
import asyncio
import json
import os
import sys

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"


async def main():
    session_str = os.environ.get("TELEGRAM_SESSION", "").strip()
    chat_id_raw = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not session_str:
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

    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("خطا: سشن معتبر نیست.")
        print("دکمه «آماده‌سازی برای گیت‌هاب» رو دوباره بزن، مقدار جدید رو کپی کن و Secret رو عوض کن.")
        print("(اگه برنامه میو‌سندر هم‌زمان بازه، ببندش — همون سشن از دو جا نمی‌تونه استفاده بشه)")
        sys.exit(1)

    me = await client.get_me()
    entity = await client.get_entity(chat_id)
    await client.send_message(entity, text)
    print(f"OK: «{text}» به {chat_id} فرستاده شد (اکانت: {me.first_name})")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
