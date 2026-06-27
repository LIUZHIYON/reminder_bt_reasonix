# -*- coding: utf-8 -*-
import urllib.request, json, time, os, subprocess

BOARD = "192.168.1.107"
WEB_PORT = 8080

def speak(text):
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
            "Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('" + text + "'); $s.Dispose()"],
            timeout=15, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[PLAY] " + text)
    except Exception as e:
        print("[PLAY ERR] " + str(e))

def main():
    print("PC Player started. Board: " + BOARD + ":" + str(WEB_PORT))
    last = set()
    while True:
        try:
            data = json.loads(urllib.request.urlopen(
                "http://" + BOARD + ":" + str(WEB_PORT) + "/api/reminders", timeout=5).read())
            for r in data:
                rid = r.get("id", "")
                if r.get("status") == "triggered" and rid not in last:
                    text = r.get("title", "")
                    if r.get("content"):
                        text += "." + r.get("content")
                    speak(text)
                    last.add(rid)
                    if len(last) > 100:
                        last = set(list(last)[-50:])
            time.sleep(2)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("[ERR] " + str(e))
            time.sleep(5)

if __name__ == "__main__":
    main()