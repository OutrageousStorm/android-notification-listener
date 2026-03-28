#!/usr/bin/env python3
"""
notif_dump.py -- Dump current Android notification list via ADB dumpsys
Outputs all active notifications with package, title, text, time.
Usage: python3 notif_dump.py [--output notifications.json] [--filter pkg]
"""
import subprocess, re, json, argparse, sys
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout

def parse_notifications(raw):
    notifications = []
    current = {}
    for line in raw.splitlines():
        line = line.strip()

        # New notification block
        pkg_m = re.match(r'NotificationRecord\(.*?pkg=(\S+)', line)
        if pkg_m:
            if current:
                notifications.append(current)
            current = {'pkg': pkg_m.group(1), 'title': '', 'text': '', 'time': '', 'channel': ''}
            continue

        if not current:
            continue

        # Title
        t = re.search(r'android\.title=(.+)', line)
        if t: current['title'] = t.group(1).strip()

        # Text
        tx = re.search(r'android\.text=(.+)', line)
        if tx: current['text'] = tx.group(1).strip()

        # Time
        tm = re.search(r'when=(\d+)', line)
        if tm:
            try:
                ts = int(tm.group(1)) / 1000
                current['time'] = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass

        # Channel
        ch = re.search(r'channel=Channel\{.*?id=([^,}]+)', line)
        if ch: current['channel'] = ch.group(1)

        # App name
        an = re.search(r'app=([^\s,]+)', line)
        if an and not current.get('app'): current['app'] = an.group(1)

    if current:
        notifications.append(current)
    return [n for n in notifications if n.get('pkg')]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Save to JSON file")
    parser.add_argument("--filter", help="Filter by package keyword")
    args = parser.parse_args()

    print("📋 Dumping notifications...")
    raw = adb("dumpsys notification --noredact")
    notifs = parse_notifications(raw)

    if args.filter:
        notifs = [n for n in notifs if args.filter.lower() in n.get('pkg','').lower()]

    if not notifs:
        print("No notifications found.")
        return

    print(f"\nFound {len(notifs)} notification(s)\n")
    print(f"{'App':<30} {'Title':<30} {'Time'}")
    print("─" * 75)
    for n in notifs:
        pkg = n.get('pkg','')
        label = pkg.split('.')[-1] if '.' in pkg else pkg
        title = n.get('title','') or n.get('text','') or '(empty)'
        time_s = n.get('time','')
        print(f"{label:<30} {title[:29]:<30} {time_s}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(notifs, f, indent=2)
        print(f"\n✅ Saved to {args.output}")

if __name__ == "__main__":
    main()
