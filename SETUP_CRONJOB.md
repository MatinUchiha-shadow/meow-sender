# راهنمای ارسال دقیق هر ۵ دقیقه (cron-job.org)

کرون خودِ گیتهاب نامطمئنه (گاهی تا ۱ ساعت دیر اجرا میشه). برای اینکه «میو» **دقیقاً** هر ۵ دقیقه بره، از سرویس رایگان **cron-job.org** استفاده میکنیم که هر ۵ دقیقه به گیتهاب میگه «الان بفرست». این فقط **یک بار** انجام میشه.

---

## قدم ۱ — ساخت توکن (فقط یک بار)

> ⚠️ **مهم:** از توکنی که توی برنامهی دسکتاپ هست استفاده نکن — اون دسترسی خیلی زیادی داره. یه توکن مخصوص همین کار بساز.

1. به [github.com/settings/tokens?type=beta](https://github.com/settings/tokens?type=beta) برو (Fine-grained tokens).
2. دکمه **Generate new token** رو بزن.
3. نام دلخواه بذار (مثلاً `meow-cron`).
4. توی **Repository access** گزینه **Only select repositories** رو بزن و ریپازیتوری `meow-sender` رو انتخاب کن.
5. توی **Permissions** برو به **Repository permissions**:
   - **Actions** → **Read and write**
   - **Metadata** → **Read-only** (خودش انتخاب میشه)
6. بقیه رو دست نزن. دکمه **Generate token** رو بزن.
7. توکنی که میگیری (شبیه `github_pat_...`) رو یهجا کپی کن — **بعد از بستن صفحه دیگه نشون داده نمیشه.**

---

## قدم ۲ — ساخت حساب cron-job.org (رایگان)

1. به [cron-job.org/en/signup/](https://cron-job.org/en/signup/) برو و با ایمیلت ثبتنام کن.
2. ایمیلت رو تأیید کن و وارد حساب شو.

---

## قدم ۳ — ساخت کرونجاب

1. از منوی **Cronjobs** دکمه **Create cronjob** رو بزن.
2. این مقادیر رو دقیق پر کن:

   **URL:**
   ```
   https://api.github.com/repos/MatinUchiha-shadow/meow-sender/actions/workflows/telegram-schedule.yml/dispatches
   ```

   **Request method:** `POST`

   **Schedule:** تیک **Custom** رو بزن و اینو بنویس:
   ```
   */5 * * * *
   ```

3. بخش **Advanced** (یا **Options**) رو باز کن و این هدرها رو اضافه کن:

   | Name | Value |
   |---|---|
   | `Authorization` | `Bearer <توکنی که ساختی>` |
   | `Accept` | `application/vnd.github+json` |
   | `Content-Type` | `application/json` |
   | `X-GitHub-Api-Version` | `2022-11-28` |

   و توی **Request body** بنویس:
   ```json
   {"ref":"main"}
   ```

4. دکمه **Create cronjob** رو بزن.

---

## قدم ۴ — تست

بعد از ذخیره، چند دقیقه صبر کن و چک کن:
- از این لینک: https://github.com/MatinUchiha-shadow/meow-sender/actions — باید هر ۵ دقیقه یه ران جدید با **event: workflow_dispatch** بیاد.
- توی گروهها، «میو» باید هر ۵ دقیقه برسه.

اگر خطایی دیدی، توی cron-job.org روی کرونجاب کلیک کن و **Executions** رو ببین — پیام خطا اونجا میاد (مثلاً 401 یعنی توکن اشتباهه).

---

## نکتهها

- cron-job.org رایگانه و محدودیت تعداد کرونجاب نداره.
- اگه یه روز فرستادن متوقف شد: اول این صفحه رو چک کن https://github.com/MatinUchiha-shadow/meow-sender/actions — اگه رانی نمیاد، توی cron-job.org وضعیت کرونجاب رو ببین (اگه ۲۵ بار متوالی خطا بده، خودش غیرفعالش میکنه).
- تغییر متن پیام: فایل `schedule.json` توی ریپازیتوری رو ویرایش کن و push کن.
- عوض کردن زمان: کافیه توی cron-job.org کرون رو عوض کنی (مثلاً `*/10 * * * *` = هر ۱۰ دقیقه، `*/30 * * * *` = هر ۳۰ دقیقه).
- گروههای بیشتر: توی Secret به نام `TELEGRAM_CHAT_ID` آیدی گروهها رو با ویرگول جدا کن (مثلاً `-1003713917910,-1003870033750`) — به همهی اونها فرستاده میشه.
