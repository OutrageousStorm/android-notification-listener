#!/usr/bin/env python3
"""
batch_notif_extract.py -- Extract all notification history from a device
Useful for forensics, analyzing notification patterns, app behavior analysis.
Usage: python3 batch_notif_extract.py --output notifications_dump.json --last-hours 24
"""
import subprocess, re, json, argparse, sys
from datetime import datetime, timedelta

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout

def extract_notifications(hours=24):
    print(f"Extracting notifications from last {hours} hours...")
    
    # Use bugreport to get notification history
    raw = adb("dumpsys notification --noredact")
    
    cutoff = datetime.now() - timedelta(hours=hours)
    notifications = []
    
    current = {}
    for line in raw.splitlines():
        # Track current notification record
        if "NotificationRecord" in line:
            if current:
                notifications.append(current)
            current = {"timestamp": datetime.now().isoformat(), "text": ""}
            continue
        
        if not current:
            continue
        
        # Extract fields
        pkg_m = re.search(r'pkg=(\S+)', line)
        if pkg_m: current['pkg'] = pkg_m.group(1)
        
        time_m = re.search(r'when=(\d+)', line)
        if time_m:
            try:
                ts = int(time_m.group(1)) / 1000
                dt = datetime.fromtimestamp(ts)
                if dt > cutoff:
                    current['timestamp'] = dt.isoformat()
            except:
                pass
        
        title_m = re.search(r'ticker=(.+)', line)
        if title_m: current['title'] = title_m.group(1)
        
        text_m = re.search(r'text=(.+)', line)
        if text_m: current['text'] = text_m.group(1)
        
        tag_m = re.search(r'tag=(.+)', line)
        if tag_m: current['tag'] = tag_m.group(1)
    
    if current:
        notifications.append(current)
    
    # Filter by time
    filtered = [n for n in notifications if 'timestamp' in n and n['timestamp']]
    return filtered

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--last-hours", type=int, default=24)
    args = parser.parse_args()
    
    notifs = extract_notifications(args.last_hours)
    
    with open(args.output, 'w') as f:
        json.dump(notifs, f, indent=2)
    
    print(f"✅ Extracted {len(notifs)} notifications")
    print(f"   Saved to: {args.output}")
    
    # Quick stats
    pkg_count = len(set(n.get('pkg') for n in notifs if 'pkg' in n))
    print(f"   From {pkg_count} unique apps")

if __name__ == "__main__":
    main()
