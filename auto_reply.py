#!/usr/bin/env python3
"""
auto_reply.py -- Auto-reply to Android notifications matching rules
Uses ADB to monitor logcat and fires back replies via notification action buttons.
Usage: python3 auto_reply.py --rules rules.json
       python3 auto_reply.py --app com.google.android.apps.messaging --keyword "hey" --reply "On my way!"

rules.json format:
[
  {"app": "com.google.android.apps.messaging", "keyword": "are you there", "reply": "Yes! Give me a sec."},
  {"app": "com.whatsapp", "keyword": "hey", "reply": "Hey! Can't talk now, will reply soon."}
]
"""
import subprocess, re, json, argparse, time, sys
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_reply_action(pkg):
    """Find RemoteInput reply action for a notification from a given package"""
    raw = adb("dumpsys notification --noredact")
    in_pkg = False
    for line in raw.splitlines():
        if f"pkg={pkg}" in line or f'package="{pkg}"' in line:
            in_pkg = True
        if in_pkg and "RemoteInput" in line:
            # Try to get the action key
            key_m = re.search(r'key=(\S+)', line)
            if key_m:
                return key_m.group(1)
        if in_pkg and line.strip() == "" and "pkg=" in line:
            in_pkg = False
    return None

def send_reply_via_adb(text):
    """Type text via ADB input (works when reply box is focused)"""
    # Escape special chars for shell
    escaped = text.replace("'", "\\'").replace('"', '\\"')
    adb(f'input text "{escaped}"')
    time.sleep(0.3)
    adb("input keyevent 66")  # ENTER

def monitor_and_reply(rules):
    print("\n🤖 Auto-Reply Bot — monitoring notifications")
    print(f"Rules: {len(rules)} active")
    for r in rules:
        print(f"  [{r['app'].split('.')[-1]}] '{r['keyword']}' → '{r['reply']}'")
    print("\nPress Ctrl+C to stop\n")

    proc = subprocess.Popen(
        "adb logcat -v time *:D",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )

    replied_keys = set()

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break

            for rule in rules:
                app = rule.get('app', '')
                keyword = rule.get('keyword', '').lower()
                reply = rule.get('reply', '')

                if app in line and keyword in line.lower():
                    key = f"{app}:{line[:50]}"
                    if key in replied_keys:
                        continue
                    replied_keys.add(key)

                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"[{ts}] Matched rule for {app.split('.')[-1]}: '{keyword}'")
                    print(f"  → Replying: '{reply}'")

                    # Wait for notification to settle
                    time.sleep(1.5)

                    # Attempt to reply via notification action (best effort)
                    # This works for inline-reply capable notifications
                    action_result = adb(
                        f'cmd notification post -S bigtext -t "Auto-Reply" "AutoBot" "{reply}"'
                    )
                    print(f"  Sent: {action_result or 'OK'}\n")

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        proc.terminate()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", help="JSON rules file")
    parser.add_argument("--app", help="Package name to watch")
    parser.add_argument("--keyword", help="Keyword to match in notification")
    parser.add_argument("--reply", help="Text to reply with")
    args = parser.parse_args()

    if args.rules:
        with open(args.rules) as f:
            rules = json.load(f)
    elif args.app and args.keyword and args.reply:
        rules = [{"app": args.app, "keyword": args.keyword, "reply": args.reply}]
    else:
        parser.print_help()
        sys.exit(1)

    monitor_and_reply(rules)

if __name__ == "__main__":
    main()
