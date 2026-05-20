#!/usr/bin/env python3
"""Quick-reply macros for notifications"""
import subprocess, sys
MACROS = {
    'busy': "I'm busy right now, will get back to you later",
    'away': "I'm away from my phone, will reply soon",
    'ok': "Got it, thanks!",
}
def send_macro(name):
    text = MACROS.get(name, name)
    subprocess.run(['adb', 'shell', 'input', 'text', text.replace(' ', '%s')])
    subprocess.run(['adb', 'shell', 'input', 'keyevent', '66'])  # ENTER
    print(f"Sent: {text}")
if __name__ == '__main__':
    macro = sys.argv[1] if len(sys.argv) > 1 else 'ok'
    send_macro(macro)
