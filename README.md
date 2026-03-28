# 🔔 Android Notification Listener

Capture, monitor, and log Android notifications via ADB — no root needed.

## Tools

| Script | What it does |
|--------|-------------|
| `notif_monitor.py` | Live notification feed from device |
| `notif_dump.py` | Dump current notification list to JSON |
| `notif_search.py` | Search notification history by app/keyword |
| `auto_reply.py` | Auto-respond to notifications matching rules |

## Requirements
```bash
pip install rich
adb devices  # device connected with USB debugging
```

## Quick start
```bash
# Live monitor
python3 notif_monitor.py

# Dump all current notifications
python3 notif_dump.py --output notifications.json

# Auto-reply to SMS from a contact
python3 auto_reply.py --app com.google.android.apps.messaging --keyword "hey" --reply "Be right back!"
```
