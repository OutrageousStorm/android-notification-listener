#!/usr/bin/env python3
"""
notif_monitor.py -- Live Android notification monitor via ADB logcat
Shows new notifications as they arrive with app name, title, and text.
Usage: python3 notif_monitor.py [--filter app.package] [--beep]
"""
import subprocess, sys, re, argparse, signal
from datetime import datetime

NOTIF_PATTERN = re.compile(
    r'NotificationManager.*?pkg=(\S+).*?'
    r'(?:title=([^,\n]+))?.*?(?:text=([^\n]+))?',
    re.IGNORECASE
)
LOGCAT_PATTERN = re.compile(
    r'(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+\d+\s+\d+\s+\w\s+(\S+)\s*:\s+(.*)'
)

def get_uid_map():
    r = subprocess.run("adb shell pm list packages -U", shell=True, capture_output=True, text=True)
    uid_map = {}
    for line in r.stdout.splitlines():
        m = re.match(r'package:(\S+)\s+uid:(\d+)', line)
        if m:
            uid_map[m.group(2)] = m.group(1)
    return uid_map

def pkg_to_label(pkg):
    """Shorten package to readable label"""
    parts = pkg.split('.')
    return parts[-1] if len(parts) > 1 else pkg

def stream_logcat(filter_pkg=None):
    uid_map = get_uid_map()
    proc = subprocess.Popen(
        "adb logcat -v time NotificationManager:D *:S",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )

    # Also watch StatusBar for a broader catch
    proc2 = subprocess.Popen(
        "adb logcat -v time StatusBarManagerService:D NotificationService:D *:S",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )

    print("\n🔔 Notification Monitor — press Ctrl+C to stop\n")
    print(f"{'Time':<12} {'App':<25} {'Title / Text'}")
    print("─" * 70)

    seen = set()
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break

            # Parse notification enqueue/post lines from dumpsys style
            if 'enqueue' in line.lower() or 'posted' in line.lower() or 'notify' in line.lower():
                pkg_m = re.search(r'pkg[=:\s]+([a-z][a-zA-Z0-9_.]+)', line)
                if pkg_m:
                    pkg = pkg_m.group(1)
                    if filter_pkg and filter_pkg not in pkg:
                        continue
                    title_m = re.search(r'title[=:\s]+(.+?)(?:\s+text=|$)', line)
                    text_m = re.search(r'text[=:\s]+(.+?)(?:\s+\w+=|$)', line)
                    title = title_m.group(1).strip() if title_m else ""
                    text = text_m.group(1).strip() if text_m else ""
                    key = f"{pkg}:{title}:{text}"
                    if key not in seen:
                        seen.add(key)
                        ts = datetime.now().strftime("%H:%M:%S")
                        label = pkg_to_label(pkg)
                        content = title or text or "(notification)"
                        print(f"{ts:<12} {label:<25} {content[:60]}")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        proc.terminate()
        proc2.terminate()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", help="Filter by package name keyword")
    args = parser.parse_args()
    stream_logcat(args.filter)

if __name__ == "__main__":
    main()
