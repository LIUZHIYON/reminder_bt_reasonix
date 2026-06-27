# -*- coding: utf-8 -*-
"""PC local proxy via SSH -> board localhost:8080"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Use paramiko to SSH-exec curl on the board
import paramiko

BOARD = "192.168.1.107"
USER = "cat"
PASS = "temppwd"
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

def ssh_exec(cmd):
    """Execute command on board and return stdout"""
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(BOARD, username=USER, password=PASS, timeout=10)
    _, out, _ = c.exec_command(cmd, timeout=10)
    result = out.read().decode()
    c.close()
    return result

class H(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        b = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _file(self, path, ct):
        if not os.path.exists(path): self.send_error(404); return
        with open(path, "rb") as f: d = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(d)))
        self.end_headers()
        self.wfile.write(d)

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/api/reminders":
            try:
                raw = ssh_exec("curl -s http://127.0.0.1:8080/api/reminders")
                data = json.loads(raw)
                return self._json(data)
            except Exception as e:
                return self._json({"error": str(e)}, 502)
        if p.path in ("/", "/index.html"):
            return self._file(os.path.join(WEB_DIR, "board_view.html"), "text/html; charset=utf-8")
        self.send_error(404)

    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        if p.path == "/api/reminders":
            j = json.dumps(body).replace("'", "'\\''")
            try:
                raw = ssh_exec(f"curl -s -X POST http://127.0.0.1:8080/api/reminders -H 'Content-Type: application/json' -d '{j}'")
                return self._json(json.loads(raw), 201)
            except Exception as e:
                return self._json({"error": str(e)}, 502)
        self.send_error(404)

    def log_message(self, *a): pass

if __name__ == "__main__":
    print("Local proxy (SSH): http://localhost:8080")
    HTTPServer(("127.0.0.1", 8080), H).serve_forever()