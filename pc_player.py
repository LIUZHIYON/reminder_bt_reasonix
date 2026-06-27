# pc_player.py - 监听板子行为树，触发时在PC播放语音
import zmq, struct, time, json, urllib.request, os, subprocess, threading

BOARD = "192.168.1.107"
ZMQ_PORT = 1669
WEB_PORT = 8000

def speak(text):
    """在PC上播放语音（Windows TTS）"""
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('{text}'); $s.Dispose()"],
            timeout=15, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[PLAY] {text}")
    except Exception as e:
        print(f"[PLAY ERR] {e}")

def main():
    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.setsockopt(zmq.RCVTIMEO, 2000)
    s.connect(f"tcp://{BOARD}:{ZMQ_PORT}")

    print(f"Connected to {BOARD}:{ZMQ_PORT}")
    print("Monitoring reminders...")

    last_played = set()

    while True:
        try:
            # Get reminder list from web API
            data = json.loads(urllib.request.urlopen(
                f"http://{BOARD}:{WEB_PORT}/api/reminders", timeout=5).read())

            for r in data:
                rid = r.get("id", "")
                status = r.get("status", "")
                title = r.get("title", "")
                if status == "triggered" and rid not in last_played:
                    text = f"{title}"
                    if r.get("content"):
                        text += f"。{r['content']}"
                    speak(text)
                    last_played.add(rid)
                    # Keep only last 100
                    if len(last_played) > 100:
                        last_played = set(list(last_played)[-50:])

            time.sleep(2)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERR] {e}")
            time.sleep(5)

    s.close()
    ctx.term()

if __name__ == "__main__":
    main()