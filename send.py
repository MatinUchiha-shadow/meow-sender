#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ارسال خودکار پیام به گروه تلگرام با اکانت خودت — نسخه رایگان و همیشه‌روشن
=====================================================================
این اسکریپت روی GitHub Actions اجرا می‌شه (سرورهای خود گیتهاب، رایگان).
هر بار که اجرا بشه (کرون توی workflow تعیین می‌کنه، مثلاً هر ۱۶ دقیقه)،
متن schedule.json رو با خود اکانتت به گروهی که عضوِش هستی می‌فرسته.

نیازمندی: یک سشن که با make_session.py ساخته شده، به صورت Secret
در گیت‌هاب با اسم TELEGRAM_SESSION ذخیره شده باشه.
"""
import asyncio
import base64
import json
import os
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from telethon import TelegramClient

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"


async def send_via_session(session_b64, chat, text):
    """وصل شدن با اکانت خودت (سشن) و فرستادن پیام به گروه."""
    with tempfile.TemporaryDirectory() as td:
        sess_path = Path(td) / "session"
        sess_path.write_bytes(base64.b64decode(session_b64))
        client = TelegramClient(str(sess_path), API_ID, API_HASH)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                raise RuntimeError("سشن معتبر نیست — دوباره make_session.py را اجرا کن")
            entity = await client.get_entity(chat)
            await client.send_message(entity, text)
            return None
        finally:
            await client.disconnect()


async def main():
    session_b64 = os.environ.get("TELEGRAM_SESSION", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not session_b64 or not chat:
        print("خطا: TELEGRAM_SESSION و TELEGRAM_CHAT_ID تنظیم نشده‌ان")
        sys.exit(1)

    if not os.path.exists("schedule.json"):
        print("خطا: schedule.json پیدا نشد")
        sys.exit(1)
    with open("schedule.json", encoding="utf-8") as f:
        schedule = json.load(f)

    text = schedule.get("text", "میو")

    err = await send_via_session(session_b64, chat, text)
    if err:
        print("خطا در ارسال:", err)
        sys.exit(1)
    print(f"✓ پیام با اکانت خودت فرستاده شد: {text[:40]}…")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nلغو شد.")
        sys.exit(1)
