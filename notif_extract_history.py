#!/usr/bin/env python3
"""
notif_extract_history.py -- Extract full notification history from device
Parses notification log and exports to JSON/CSV with timestamps.
Usage: python3 notif_extract_history.py [--output history.json] [--days 7]
"""
import subprocess, re, json, csv, argparse
from datetime import datetime, timedelta

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def extract_history(days=7):
    cutoff = datetime.now() - timedelta(days=days)
    
    # Try notification log via dumpsys
    raw = adb("dumpsys notification --noredact")
    notifications = []
    
    for line in raw.splitlines():
        # Extract individual notification entries
        if "NotificationRecord" in line:
            pkg_m = re.search(r'pkg=(\S+)', line)
            time_m = re.search(r'when=(\d+)', line)
            title_m = re.search(r'title=([^,\n]+)', line)
            text_m = re.search(r'text=([^,\n]+)', line)
            
            if pkg_m and time_m:
                try:
                    ts = int(time_m.group(1)) / 1000
                    dt = datetime.fromtimestamp(ts)
                    if dt > cutoff:
                        notifications.append({
                            'package': pkg_m.group(1),
                            'title': title_m.group(1) if title_m else '',
                            'text': text_m.group(1) if text_m else '',
                            'timestamp': dt.isoformat(),
                            'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                        })
                except Exception:
                    pass
    
    return notifications

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Output file (JSON or CSV based on extension)")
    parser.add_argument("--days", type=int, default=7, help="Look back N days")
    args = parser.parse_args()

    print(f"📋 Extracting {args.days} days of notification history...")
    notifs = extract_history(args.days)

    print(f"\nFound {len(notifs)} notifications\n")
    print(f"{'App':<25} {'Time':<20} {'Title/Text'}")
    print("─" * 75)
    for n in notifs[:20]:
        pkg = n['package'].split('.')[-1]
        content = n['title'] or n['text'] or '(empty)'
        print(f"{pkg:<25} {n['time']:<20} {content[:40]}")

    if args.output:
        if args.output.endswith('.csv'):
            with open(args.output, 'w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=['package', 'title', 'text', 'time'])
                w.writeheader()
                w.writerows(notifs)
        else:
            with open(args.output, 'w') as f:
                json.dump(notifs, f, indent=2)
        print(f"\n✅ Saved to {args.output}")

if __name__ == "__main__":
    main()
