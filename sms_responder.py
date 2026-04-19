#!/usr/bin/env python3
"""
sms_responder.py -- Auto-reply to incoming SMS messages
Watches SMS notifications and fires templated replies.
Usage: python3 sms_responder.py --rules sms_rules.json --dry-run
"""
import subprocess, re, json, argparse, time, sys
from datetime import datetime
from pathlib import Path

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def adb_put(cmd):
    subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True)

def get_sms_apps():
    """Find installed SMS apps"""
    apps = {
        "messaging": "com.google.android.apps.messaging",
        "samsung": "com.samsung.android.messaging",
        "stock": "com.android.messaging",
    }
    installed = {}
    for name, pkg in apps.items():
        if adb(f"pm list packages {pkg}"):
            installed[name] = pkg
    return installed

def send_sms(phone, message, dry_run=False):
    """Send SMS via adb (requires default SMS app)"""
    if dry_run:
        print(f"  [DRY] SMS to {phone}: {message}")
        return True
    # Use content provider to queue SMS
    cmd = f'am start -a android.intent.action.SENDTO -d "sms:{phone}" --es sms_body "{message}"'
    adb_put(cmd)
    time.sleep(1)
    # Simulate send
    adb_put("input keyevent 66")  # ENTER
    return True

def monitor_sms(rules, dry_run=False):
    """Monitor SMS notifications and auto-reply"""
    print(f"\n📲 SMS Auto-Responder — {len(rules)} rules active")
    print("Monitoring... (Ctrl+C to stop)\n")

    sms_apps = get_sms_apps()
    if not sms_apps:
        print("No SMS app installed")
        return

    seen_sms = set()
    proc = subprocess.Popen(
        "adb logcat -v time *:D",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break

            # Look for SMS notification patterns
            if any(app in line for app in sms_apps.values()):
                for rule in rules:
                    keyword = rule.get("keyword", "").lower()
                    phone = rule.get("from_phone", "")
                    reply = rule.get("reply", "")

                    if keyword and keyword in line.lower():
                        key = f"{phone}:{line[:40]}"
                        if key in seen_sms:
                            continue
                        seen_sms.add(key)

                        ts = datetime.now().strftime("%H:%M:%S")
                        print(f"[{ts}] SMS matched: '{keyword}'")
                        print(f"  → Replying to {phone}: {reply}")

                        if not dry_run:
                            send_sms(phone, reply)
                        print()

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        proc.terminate()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", required=True, help="JSON rules file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be sent without sending")
    args = parser.parse_args()

    with open(args.rules) as f:
        rules = json.load(f)

    monitor_sms(rules, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
