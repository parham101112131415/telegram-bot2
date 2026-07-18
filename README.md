# YouTube Downloader Bot — Railway Deployment

## مراحل deploy روی Railway

### ۱. ساخت پروژه جدید
- به [railway.app](https://railway.app) برو و وارد شو
- روی **New Project** کلیک کن
- گزینه **Deploy from GitHub repo** یا **Deploy from local** رو انتخاب کن

### ۲. آپلود فایل‌ها
- همه فایل‌های این پوشه رو به Railway آپلود کن
- یا یه repo گیت‌هاب بساز و اونجا push کن

### ۳. تنظیم Environment Variables
در Railway → Settings → Variables این متغیر رو اضافه کن:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | توکن ربات تلگرامت |

> **WEBHOOK_URL** نیازی نیست دستی تنظیم کنی — Railway خودکار از `RAILWAY_PUBLIC_DOMAIN` می‌خونه.

### ۴. Deploy
Railway خودکار build و deploy می‌کنه. بعد از چند دقیقه یه آدرس مثل:
```
https://your-app.railway.app
```
می‌گیری. ربات webhook رو روی همون آدرس تنظیم می‌کنه.

## دستورات ربات
- `/start` — شروع
- `/video` + لینک یوتیوب → دانلود ویدیو MP4  
- `/audio` + لینک یوتیوب → دانلود صدا MP3
