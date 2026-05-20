#!/usr/bin/env python3
"""Quick-reply to notifications with predefined macros"""
import subprocess, time

MACROS = {
    '1': 'I'm driving, will call you back',
    '2': 'In a meeting, text you later',
    '3': 'Got it, thanks!',
    '4': 'On my way',
}

def send_reply(text):
    subprocess.run(['adb', 'shell', 'input', 'text', text], check=False)
    time.sleep(0.2)
    subprocess.run(['adb', 'shell', 'input', 'keyevent', '66'], check=False)

print("Quick macros:")
for k, v in MACROS.items():
    print(f"  {k}: {v}")

choice = input("Select (1-4): ")
if choice in MACROS:
    send_reply(MACROS[choice])
    print("✓ Sent")
