#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ارسال خودکار روی GitHub Actions — ۲۴ ساعته و رایگان، حتی با لپ‌تاپ خاموش
========================================================================
نحوه کار:
  - متن (`text`)، فاصله ارسال (`interval_min`) و مقصد (`target`) از schedule.json خونده می‌شه
  - مقصد: آیدی عددی، یوزرنیم یا لینک گروه (مثل t.me/Your_Fragment53) —
    اگه توی schedule.json نبود، از Secret به نام TELEGRAM_CHAT_ID استفاده می‌شه
  - فاصله ارسال خودِ send.py کنترل می‌شه: آخرین زمان ارسال توی state.json ذخیره
    می‌شه و تا وقتی `interval_min` نگذشته، دوباره چیزی نمی‌فرسته
  - سشن اکانتت (که با دکمه «آماده‌سازی برای گیت‌هاب» داخل میو‌سندر کپی شد)
    به صورت StringSession از Secret به نام TELEGRAM_SESSION خونده می‌شه

اجرای تست لوکال:
    TELEGRAM_SESSION=<string> python send.py
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

STATE_FILE = "state.json"


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


async def main():
    session_str = os.environ.get("TELEGRAM_SESSION", "").strip()
    chat_id_raw = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not session_str:
        print("خطا: Secret به نام TELEGRAM_SESSION تنظیم نشده.")
        sys.exit(1)

    try:
        with open("schedule.json", encoding="utf-8") as f:
            sched = json.load(f)
        text = sched.get("text", "ماهی")
        target = sched.get("target", "").strip()
        interval_min = sched.get("interval_min", 90)
    except Exception as e:
        print(f"خطا: schedule.json خونده نشد — {e}")
        sys.exit(1)

    try:
        interval_secs = max(1, int(interval_min)) * 60
    except Exception:
        interval_secs = 90 * 60

    # بازه ارسال: اگه هنوز وقتش نرسیده، چیزی نمی‌فرسته
    now = time.time()
    state = load_state()
    try:
        last = float(state.get("last_sent", 0) or 0)
    except Exception:
        last = 0
    due_at = last + interval_secs
    if now < due_at:
        nxt = datetime.utcfromtimestamp(due_at).strftime("%Y-%m-%d %H:%M UTC")
        print(f"هنوز وقتش نشده — ارسال بعدی: {nxt} (هر {interval_secs // 60} دقیقه)")
        return

    # مقصد: اول از schedule.json، بعد Secret (چند گروه با ویرگول)
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

    state["last_sent"] = now
    save_state(state)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
