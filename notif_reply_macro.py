#!/usr/bin/env python3
"""notif_reply_macro.py -- Quick-reply macros for Android notifications
Press number on device to send pre-written response to incoming message
"""
import subprocess, json, time

MACROS = {
    "1": {"reply": "On my way! 🚗", "apps": ["messaging", "whatsapp"]},
    "2": {"reply": "Can't talk now, will call back", "apps": ["messaging", "whatsapp"]},
    "3": {"reply": "Got it, thanks!", "apps": ["messaging", "whatsapp"]},
    "4": {"reply": "Send me the details", "apps": ["messaging", "whatsapp"]},
}

def adb(cmd):
    subprocess.run(['adb', 'shell'] + cmd.split(), capture_output=True)

def watch_keys():
    """Watch for number keys pressed on device"""
    proc = subprocess.Popen(['adb', 'shell', 'getevent'], 
                           stdout=subprocess.PIPE, text=True)
    print("Watching for macro keypresses (1-4)...")
    for line in proc.stdout:
        if 'KEY_' in line:
            for num in MACROS.keys():
                if f'KEY_{num}' in line:
                    reply = MACROS[num]["reply"]
                    print(f"🔴 Macro {num}: {reply}")
                    # Try to send reply via notification action
                    adb(f'input text "{reply}"')
                    time.sleep(0.2)
                    adb('input keyevent 66')

if __name__ == '__main__':
    watch_keys()
