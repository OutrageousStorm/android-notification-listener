#!/usr/bin/env python3
"""Define hotkeys to auto-reply to notifications"""
import subprocess, json, time

MACROS = {
    'ctrl+shift+1': {'text': 'Can\'t talk now, will call back soon'},
    'ctrl+shift+2': {'text': 'On my way'},
    'ctrl+shift+3': {'text': 'Thanks! Got it'},
}

def send_quick_reply(text):
    """Send reply via ADB input"""
    subprocess.run(['adb', 'shell', 'input', 'text', text])
    subprocess.run(['adb', 'shell', 'input', 'keyevent', '66'])  # ENTER

print("Notification hotkey macros set:")
for hotkey, action in MACROS.items():
    print(f"  {hotkey}: '{action['text']}'")
print("(Requires third-party hotkey daemon like AutoHotkey)")
