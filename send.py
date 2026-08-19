#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ارسال خودکار «میو» روی GitHub Actions — ۲۴ ساعته و رایگان، حتی با لپ‌تاپ خاموش
==============================================================================
نحوه کار:
  - متن پیام از schedule.json خونده می‌شه
  - مقصد از schedule.json و کلید target خونده می‌شه (آیدی عددی، یوزرنیم یا لینک گروه)
    — اگه اونجا نبود، از Secret به نام TELEGRAM_CHAT_ID استفاده می‌شه
    (Secret می‌تونه چند گروه با ویرگول باشه: -100111,-100222)
  - سشن اکانتت (که با دکمه «آماده‌سازی برای گیت‌هاب» داخل میو‌سندر کپی شد)
    به صورت StringSession از Secret به نام TELEGRAM_SESSION خونده می‌شه

اجرای تست لوکال:
    TELEGRAM_SESSION=<string> python send.py
    (با کلید target توی schedule.json یا TELEGRAM_CHAT_ID=<...>)
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

    try:
        with open("schedule.json", encoding="utf-8") as f:
            sched = json.load(f)
        text = sched.get("text", "میو")
        target = sched.get("target", "").strip()
    except Exception as e:
        print(f"خطا: schedule.json خونده نشد — {e}")
        sys.exit(1)

    # مقصد: اول از schedule.json (آیدی، یوزرنیم یا لینک گروه)، بعد Secret
    targets = [target] if target else [p.strip() for p in chat_id_raw.split(",") if p.strip()]
    if not targets:
        print("خطا: مقصد مشخص نیست — توی schedule.json کلید target رو بذار\n"
              "یا Secret به نام TELEGRAM_CHAT_ID رو تنظیم کن.")
        sys.exit(1)

    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("خطا: سشن معتبر نیست.")
        print("دکمه «آماده‌سازی برای گیت‌هاب» رو دوباره بزن، مقدار جدید رو کپی کن و Secret رو عوض کن.")
        print("(اگه برنامه میو‌سندر هم‌زمان بازه، ببندش — همون سشن از دو جا نمی‌تونه استفاده بشه)")
        sys.exit(1)

    me = await client.get_me()
    for t in targets:
        try:
            chat_id = int(t)   # آیدی عددی مثل -1001234567890
        except ValueError:
            chat_id = t        # یوزرنیم یا لینک مثل t.me/Your_Fragment53
        entity = await client.get_entity(chat_id)
        await client.send_message(entity, text)
        print(f"OK: «{text}» به {t} فرستاده شد (اکانت: {me.first_name})")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
