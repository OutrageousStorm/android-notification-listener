#!/usr/bin/env python3
import subprocess, re
from collections import defaultdict
def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()
apps = defaultdict(int)
for line in adb("dumpsys notification --noredact").split("\n"):
    m = re.search(r"pkg=([a-z][a-zA-Z0-9_.]+)", line)
    if m: apps[m.group(1)] += 1
print("\n[Top Notification Senders]\n")
for app, cnt in sorted(apps.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {cnt:3d}x {app.split('.')[-1]}")
