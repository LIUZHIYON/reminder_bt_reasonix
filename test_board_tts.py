# reminder_bt PC测试脚本
# 板子edge-tts合成语音 -> 下载到PC -> PC喇叭播放

import paramiko, time, os, sys

BOARD = "192.168.1.107"
USER = "cat"
PASS = "temppwd"
TEXT = sys.argv[1] if len(sys.argv) > 1 else "小明该吃饭啦"

print(f"Connecting to {BOARD}...")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(BOARD, username=USER, password=PASS, timeout=10)

# Generate TTS on board
c.exec_command("cat > /tmp/_tts_gen.py << 'EOF'\nimport edge_tts,asyncio\nasync def r():\n c=edge_tts.Communicate('" + TEXT + "','zh-CN-XiaoyiNeural')\n await c.save('/tmp/_tts_out.mp3')\nasyncio.run(r())\nprint('OK')\nEOF", timeout=5)
_, out, _ = c.exec_command("timeout 20 python3 /tmp/_tts_gen.py 2>&1", timeout=25)
if "OK" not in out.read().decode():
    print("TTS failed"); c.close(); exit()

# Convert
c.exec_command("ffmpeg -y -i /tmp/_tts_out.mp3 -acodec pcm_s16le -ar 22050 -ac 1 /tmp/_tts_out.wav 2>/dev/null", timeout=10)

# Download
local = r"E:\LuBanCat\BT_ros2\reminder_bt\_board_tts.wav"
sftp = c.open_sftp()
sftp.get("/tmp/_tts_out.wav", local)
sftp.close()
c.close()

# Play on PC
import subprocess
subprocess.run(["powershell", "-Command",
    "(New-Object System.Media.SoundPlayer '" + local + "').PlaySync()"],
    timeout=15)
print(f"Done! Played: {TEXT}")